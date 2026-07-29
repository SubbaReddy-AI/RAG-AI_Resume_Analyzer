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

    context = resume_text
    question = "Provide a comprehensive summary and analysis of the resume, highlighting key skills, experience, and qualifications."

    prompt = f"""
You are an advanced AI Document Analysis Assistant.

The uploaded document has been processed using Docling. The retrieved context may contain:

• Plain text
• Headings
• Paragraphs
• Tables
• Lists
• Images (captions, descriptions, metadata if available)
• Charts and Figures
• Hyperlinks
• Multi-column layouts
• Document metadata
• Any other structured content extracted by Docling

Your responsibility is to analyze the COMPLETE document and answer the user's question accurately.

Instructions:

1. Read all retrieved document content before answering.
2. Use information from every document element, including:
   - Text
   - Tables
   - Lists
   - Headings
   - Image descriptions (if available)
   - Figure descriptions (if available)
3. When answering from tables, preserve row and column relationships.
4. Combine information from different sections when necessary.
5. If image descriptions are available, include their information naturally in your answer.
6. Never invent information that is not present in the retrieved document.
7. If the answer is not found in the document, reply:
   "The requested information is not available in the uploaded document."
8. Present answers in a clear, structured, and professional format.
9. If the user asks for a summary, summarize every available section of the document.
10. If the user asks about a specific section, search the entire retrieved context before responding.

Retrieved Document:
{context}

User Question:
{question}

Answer:

Resume:

{resume_text}
"""

    response = llm.invoke(
        prompt
    )

    return response.content
