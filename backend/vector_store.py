from langchain_community.vectorstores import FAISS

from embeddings import get_embedding_model


def create_vector_store(chunks):
    """
    Convert document chunks into embeddings
    and store them in FAISS.
    """

    if not chunks:
        raise ValueError(
            "No document chunks were provided."
        )

    embeddings = get_embedding_model()

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vector_store


def get_retriever(vector_store):
    """
    Create a retriever from the FAISS
    vector database.
    """

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 4
        }
    )

    return retriever