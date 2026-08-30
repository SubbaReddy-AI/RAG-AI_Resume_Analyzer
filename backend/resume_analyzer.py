from rag_chain import get_llm


def analyze_resume(documents):
    """
    Analyze the complete uploaded resume using the Groq LLM.

    This version does not depend on:
    - Docling
    - FAISS
    - Sentence Transformers
    - PyTorch
    """

    if not documents:
        return "No resume content was found."

    llm = get_llm()

    # Combine all extracted resume text
    resume_text = "\n\n".join(
        document.page_content
        for document in documents
        if document.page_content
    )

    if not resume_text.strip():
        return "No readable text was found in the resume."

    prompt = f"""
You are an advanced AI Resume Analysis Assistant.

Analyze the COMPLETE resume provided below.

Your job is to provide an accurate, professional analysis using
ONLY the information present in the resume.

IMPORTANT RULES:

1. Do not invent any information.
2. Do not assume skills, experience, education, or qualifications
   that are not explicitly present.
3. Analyze all available resume content.
4. Identify important sections such as:
   - Name
   - Contact information
   - Professional summary
   - Education
   - Technical skills
   - Soft skills
   - Work experience
   - Internships
   - Projects
   - Certifications
   - Achievements
   - Languages
   - Other relevant information
5. Clearly identify missing sections when appropriate.
6. Keep the analysis professional and easy to understand.
7. Use bullet points and headings.
8. Do not use information from outside the resume.

Provide the analysis in this structure:

## 1. Resume Summary
Give a concise overall summary.

## 2. Candidate Profile
Mention the candidate's background based only on the resume.

## 3. Education
List the education details found in the resume.

## 4. Technical Skills
List the technical skills found in the resume.

## 5. Soft Skills
List the soft skills found in the resume, if available.

## 6. Work Experience
Summarize the work experience found in the resume.

## 7. Internships
Summarize internships, if available.

## 8. Projects
Summarize the projects and technologies mentioned.

## 9. Certifications
List certifications, if available.

## 10. Achievements
List achievements, if available.

## 11. Strengths
Identify strengths supported by the resume.

## 12. Areas for Improvement
Identify reasonable resume/content improvements based only on
what is missing, unclear, or weak in the resume.

## 13. Overall Assessment
Give a concise professional assessment of the resume.

RESUME CONTENT:

{resume_text}

END OF RESUME

Now provide the complete analysis.
"""

    try:
        response = llm.invoke(prompt)

        answer = getattr(
            response,
            "content",
            str(response)
        )

        return answer.strip()

    except Exception as e:
        print(
            f"[ERROR] Resume analysis failed: {e}"
        )

        return (
            "Unable to analyze the resume at this time. "
            "Please try again."
        )