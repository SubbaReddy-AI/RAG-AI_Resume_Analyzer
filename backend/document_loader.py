from langchain_community.document_loaders import PyMuPDFLoader


def load_pdf(file_path: str):
    """
    Load a PDF file and return LangChain documents.
    """

    try:
        loader = PyMuPDFLoader(file_path)

        documents = loader.load()

        return documents

    except Exception as error:
        raise Exception(
            f"Error while reading PDF: {str(error)}"
        )