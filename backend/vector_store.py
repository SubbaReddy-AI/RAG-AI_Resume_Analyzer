import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleVectorStore:
    """
    Lightweight in-memory vector store using TF-IDF.
    No FAISS, PyTorch, Transformers, or Sentence Transformers required.
    """

    def __init__(self, documents):
        self.documents = documents

        self.texts = [
            document.page_content
            for document in documents
        ]

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2)
        )

        if self.texts:
            self.matrix = self.vectorizer.fit_transform(self.texts)
        else:
            self.matrix = None

    def similarity_search(self, query, k=5):
        """
        Return the most relevant documents for a query.
        """

        if not self.texts or self.matrix is None:
            return []

        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.matrix
        ).flatten()

        k = min(k, len(self.documents))

        # Highest similarity first
        indices = similarities.argsort()[-k:][::-1]

        return [
            self.documents[index]
            for index in indices
        ]


class SimpleRetriever:
    """
    Retriever compatible with the RAG chain.
    """

    def __init__(self, vector_store, k=5):
        self.vector_store = vector_store
        self.k = k

    def invoke(self, query):
        return self.vector_store.similarity_search(
            query,
            k=self.k
        )

    def get_relevant_documents(self, query):
        return self.vector_store.similarity_search(
            query,
            k=self.k
        )


def create_vector_store(chunks):
    """
    Create lightweight TF-IDF vector store.
    """

    if not chunks:
        raise ValueError(
            "Cannot create vector store because no document chunks were provided."
        )

    return SimpleVectorStore(chunks)


def get_retriever(vector_store):
    """
    Create lightweight retriever.

    Returns top 5 relevant resume chunks.
    """

    return SimpleRetriever(
        vector_store=vector_store,
        k=5
    )


# ---------------------------------------------------------
# Optional save/load functions
# ---------------------------------------------------------

def save_vector_store(vector_store, folder_path="vector_db"):
    """
    Save the lightweight vector store to disk.
    """

    folder = Path(folder_path)
    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = folder / "vector_store.pkl"

    with open(file_path, "wb") as file:
        pickle.dump(
            vector_store,
            file
        )


def load_vector_store(folder_path="vector_db"):
    """
    Load the lightweight vector store from disk.
    """

    file_path = (
        Path(folder_path)
        / "vector_store.pkl"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Vector store not found: {file_path}"
        )

    with open(file_path, "rb") as file:
        return pickle.load(file)