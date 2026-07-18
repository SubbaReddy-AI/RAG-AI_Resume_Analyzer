from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import (
    GROQ_API_KEY,
    LLM_MODEL
)


def get_llm():
    """
    Create the Groq LLM.
    """

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add it to your .env file."
        )

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0
    )

    return llm


def create_rag_chain(retriever):
    """
    Create a simple RAG question-answer function.
    """

    llm = get_llm()

    prompt = ChatPromptTemplate.from_template(
        """
You are an AI Resume Assistant.

Answer the user's question using only the
resume context provided below.

If the answer cannot be found in the resume,
say:

"I could not find this information in the resume."

Resume Context:
{context}

User Question:
{question}

Answer:
"""
    )

    def ask_question(question: str):

        # Search relevant resume chunks
        documents = retriever.invoke(
            question
        )

        # Combine retrieved text
        context = "\n\n".join(
            document.page_content
            for document in documents
        )

        # Create the final prompt
        messages = prompt.format_messages(
            context=context,
            question=question
        )

        # Send prompt to LLM
        response = llm.invoke(
            messages
        )

        return response.content

    return ask_question