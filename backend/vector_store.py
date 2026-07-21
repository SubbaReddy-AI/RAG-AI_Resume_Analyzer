from langchain_community.vectorstores import FAISS
from embeddings import get_embedding_model


def create_vector_store(chunks):
    embeddings = get_embedding_model()

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vector_store


def get_retriever(vector_store):
    return vector_store.as_retriever(
        search_kwargs={"k": 4}
    )