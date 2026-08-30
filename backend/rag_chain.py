from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY, GROQ_LLM_MODEL_NAME


def get_llm():
    """
    Create the Groq language model.
    """

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing."
        )

    return ChatGroq(
        model=GROQ_LLM_MODEL_NAME,
        api_key=GROQ_API_KEY,
        temperature=0
    )


def create_rag_chain(retriever):
    """
    Create a lightweight RAG question-answering function.
    """

    llm = get_llm()

    prompt = ChatPromptTemplate.from_template(
        """
You are an AI Resume Assistant.

Answer the user's question using ONLY the resume context provided below.

Rules:
1. Do not invent information.
2. Do not use outside knowledge.
3. If the answer is not available in the resume context, say:
   "I could not find this information in the resume."
4. Keep the answer clear and concise.
5. If the question asks for a list, use bullet points.

Resume Context:
{context}

Question:
{question}

Answer:
"""
    )

    def ask_question(question: str):
        """
        Retrieve relevant resume sections and ask Groq.
        """

        if not question or not question.strip():
            return "Please enter a question."

        # Retrieve relevant resume chunks
        docs = retriever.invoke(
            question.strip()
        )

        if not docs:
            return (
                "I could not find this information "
                "in the resume."
            )

        # Build context
        context_parts = []

        for doc in docs:
            text = getattr(
                doc,
                "page_content",
                ""
            )

            if text and text.strip():
                context_parts.append(
                    text.strip()
                )

        context = "\n\n---\n\n".join(
            context_parts
        )

        if not context:
            return (
                "I could not find this information "
                "in the resume."
            )

        # Create prompt messages
        messages = prompt.format_messages(
            context=context,
            question=question.strip()
        )

        # Call Groq
        response = llm.invoke(messages)

        answer = getattr(
            response,
            "content",
            str(response)
        )

        return answer.strip()

    return ask_question