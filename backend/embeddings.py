from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the embedding model once and reuse it.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )