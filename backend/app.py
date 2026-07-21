
from pathlib import Path
import shutil

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import GOOGLE_API_KEY, UPLOAD_DIR
from document_loader import load_pdf
from text_splitter import split_documents
from vector_store import (
    create_vector_store,
    get_retriever
)
from rag_chain import create_rag_chain
from resume_analyzer import analyze_resume


# ===========================
# FastAPI App
# ===========================

app = FastAPI(
    title="AI Resume RAG Assistant",
    description="AI Resume Analyzer using RAG",
    version="1.0.0"
)


# ===========================
# CORS
# ===========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
        # For production, replace "*" with:
        # "https://your-vercel-app.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# Global Variables
# ===========================

vector_store = None
rag_chain = None


# ===========================
# Request Model
# ===========================

class QuestionRequest(BaseModel):
    question: str


# ===========================
# Home Route
# ===========================

import google.generativeai as genai

@app.get("/models")
def list_models():
    genai.configure(api_key=GOOGLE_API_KEY)
    return [m.name for m in genai.list_models()]
# ===========================
# Health Check
# ===========================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ===========================
# Upload Resume
# ===========================

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    global vector_store
    global rag_chain

    try:

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        filename = Path(file.filename).name

        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        documents = load_pdf(str(file_path))

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No text found in PDF."
            )

        chunks = split_documents(documents)

        vector_store = create_vector_store(chunks)

        retriever = get_retriever(vector_store)

        rag_chain = create_rag_chain(retriever)

        analysis = analyze_resume(documents)

        return {
            "message": "Resume uploaded successfully",
            "filename": filename,
            "chunks_created": len(chunks),
            "analysis": analysis
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ===========================
# Ask Questions
# ===========================

@app.post("/ask")
def ask_resume(request: QuestionRequest):
    global rag_chain

    if rag_chain is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume before asking questions."
        )

    try:
        answer = rag_chain(request.question)

        return {
            "question": request.question,
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )