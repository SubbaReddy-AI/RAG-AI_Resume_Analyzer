from langchain_community.vectorstores import FAISS
from embeddings import get_embedding_model


def create_vector_store(chunks):
    """Creates an in-memory FAISS vector database from document chunks."""
    embeddings = get_embedding_model()

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vector_store


def get_retriever(vector_store):
    """Returns a retriever with Maximal Marginal Relevance (MMR) search.
    
    MMR retrieves relevant chunks while ensuring diversity, avoiding redundant 
    passages from the resume.
    """
    return vector_store.as_retriever(
        search_type="mmr",  # Balances relevance and diversity
        search_kwargs={
            "k": 4,           # Returns top 4 relevant chunks
            "fetch_k": 10     # Evaluates top 10 candidates before selecting top 4
        }
    )


# Optional: Helper functions to save and load vector store to disk
def save_vector_store(vector_store, folder_path="vector_db"):
    """Saves FAISS index locally."""
    vector_store.save_local(folder_path)


def load_vector_store(folder_path="vector_db"):
    """Loads FAISS index from disk."""
    embeddings = get_embedding_model()
    return FAISS.load_local(
        folder_path, 
        embeddings, 
        allow_dangerous_deserialization=True
    )