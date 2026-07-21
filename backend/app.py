import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from groq import Groq
from langchain_groq import ChatGroq
from pydantic import BaseModel

from config import BASE_DIR, GROQ_API_KEY, UPLOAD_DIR
from document_loader import load_pdf
from rag_chain import create_rag_chain
from resume_analyzer import analyze_resume
from text_splitter import split_documents
from vector_store import create_vector_store, get_retriever

# ===========================
# FastAPI App Initialization
# ===========================

app = FastAPI(
    title="AI Resume RAG Assistant",
    description="AI Resume Analyzer using RAG",
    version="1.0.0"
)

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)


# ===========================
# CORS
# ===========================

# ✅ NEW CORS CODE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://rag-ai-resume-analyzer.vercel.app",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# Static Files & Frontend Mounting
# ===========================

# Assumes index.html, style.css, script.js live in a 'frontend' directory
FRONTEND_DIR = BASE_DIR / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ===========================
# Global Variables
# ===========================

vector_store = None
rag_chain = None


# ===========================
# Request Models
# ===========================

class QuestionRequest(BaseModel):
    question: str


# ===========================
# System Routes & Frontend Root
# ===========================

@app.get("/")
def serve_frontend():
    """Serves the main HTML page for the application."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend UI available. Place index.html inside the 'frontend' directory."}


@app.get("/models")
def list_models():
    """Returns the models configured for text generation and embeddings."""
    return {
        "chat_model": "llama-3.1-8b-instant",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok"
    }


# ===========================
# Upload Resume Endpoint
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

        # Ensure upload directory exists
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
# Ask Questions Endpoint
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
        # Handles both Runnable chain format (invoke) and standard function/chain calls
        if hasattr(rag_chain, "invoke"):
            response = rag_chain.invoke(request.question)
            answer = response.content if hasattr(response, "content") else str(response)
        else:
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