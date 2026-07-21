from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY


def get_llm():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing.")

    # Fixed: Using Llama 3.1 8B Instant instead of the embedding model string
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=GROQ_API_KEY,
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
            doc.page_content for doc in docs
        )

        messages = prompt.format_messages(
            context=context,
            question=question
        )

        response = llm.invoke(messages)

        return response.content

    return ask_question