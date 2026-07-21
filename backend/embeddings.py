from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import GOOGLE_API_KEY

embedding_model = None


def get_embedding_model():
    global embedding_model

    if embedding_model is None:
        embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )

    return embedding_model