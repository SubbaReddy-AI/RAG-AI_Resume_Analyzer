from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


def load_pdf(file_path):
    """
    Lightweight PDF text extraction.
    Uses pypdf instead of Docling, PyTorch, OCR, etc.
    """

    try:
        pdf_path = Path(file_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        reader = PdfReader(str(pdf_path))

        documents = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            text = text.strip()

            if text:
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path.name,
                            "page": page_number
                        }
                    )
                )

        return documents

    except Exception as e:
        raise RuntimeError(
            f"Failed to extract PDF text: {str(e)}"
        )