from backend.config import EMBEDDING_MODEL
from langchain_openai import OpenAIEmbeddings
from config import OPENAI_API_KEY

embedding_model = None


def get_embedding_model():
    global embedding_model

    if embedding_model is None:
        embedding_model = OpenAIEmbeddings(
             model=EMBEDDING_MODEL,
            api_key=OPENAI_API_KEY
        )

    return embedding_model