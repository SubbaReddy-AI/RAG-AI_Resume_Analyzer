from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from config import (
    GOOGLE_API_KEY,
    LLM_MODEL
)


def get_llm():

    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is missing."
        )

    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0
    )

    return llm


def create_rag_chain(retriever):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_template(
        """
You are an AI Resume Assistant.

Answer the user's question only using the resume context.

If the answer is not present in the resume, say:
"I could not find this information in the resume."

Resume Context:
{context}

Question:
{question}

Answer:
"""
    )

    def ask_question(question: str):

        docs = retriever.invoke(question)

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        messages = prompt.format_messages(
            context=context,
            question=question
        )

        response = llm.invoke(messages)

        return response.content

    return ask_question