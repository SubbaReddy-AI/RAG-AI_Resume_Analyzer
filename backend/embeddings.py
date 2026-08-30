from sklearn.feature_extraction.text import TfidfVectorizer


class TfidfEmbeddings:
    """
    Lightweight local embeddings using TF-IDF.
    Does not require PyTorch, Transformers, or Sentence Transformers.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2)
        )

    def fit(self, texts):
        self.vectorizer.fit(texts)
        return self

    def embed_documents(self, texts):
        matrix = self.vectorizer.transform(texts)
        return matrix.toarray().tolist()

    def embed_query(self, text):
        vector = self.vectorizer.transform([text])
        return vector.toarray()[0].tolist()