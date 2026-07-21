from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL_NAME  # or use "sentence-transformers/all-MiniLM-L6-v2" directly

embedding_model = None


def get_embedding_model():
    global embedding_model

    if embedding_model is None:
        # Runs sentence-transformers/all-MiniLM-L6-v2 locally (~90 MB)
        # No API key required!
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    return embedding_model