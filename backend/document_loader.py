# pyrefly: ignore [missing-import]
from docling.document_converter import DocumentConverter
from langchain_core.documents import Document

converter = DocumentConverter()

def load_pdf(file_path):
    result = converter.convert(file_path)

    text = result.document.export_to_markdown()

    if not text.strip():
        return []

    return [Document(page_content=text)]