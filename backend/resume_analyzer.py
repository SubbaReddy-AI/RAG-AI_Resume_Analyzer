from rag_chain import get_llm


def analyze_resume(documents):
    """
    Analyze the resume using the LLM.
    """

    llm = get_llm()

    resume_text = "\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = f"""
You are an expert AI Resume Analyzer.

Analyze the following resume.

Give the result in this format:

1. Candidate Summary
2. Technical Skills
3. Soft Skills
4. Education
5. Work Experience
6. Projects
7. Strengths
8. Missing or Weak Areas
9. Suggestions for Improvement

Resume:

{resume_text}
"""

    response = llm.invoke(
        prompt
    )

    return response.content