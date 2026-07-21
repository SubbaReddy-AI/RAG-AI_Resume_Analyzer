from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL

embeddings = None

def get_embedding_model():
    global embeddings

    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

    return embeddings