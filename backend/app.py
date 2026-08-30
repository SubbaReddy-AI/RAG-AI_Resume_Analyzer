# ============================================================
# AI RESUME RAG ASSISTANT - FASTAPI BACKEND
# ============================================================

import os
import shutil
import asyncio
from pathlib import Path
from typing import Any

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from groq import Groq
from pydantic import BaseModel

from config import (
    BASE_DIR,
    GROQ_API_KEY,
    GROQ_LLM_MODEL_NAME,
    UPLOAD_DIR,
)

from document_loader import load_pdf
from rag_chain import create_rag_chain
from text_splitter import split_documents
from vector_store import create_vector_store, get_retriever


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Resume RAG Assistant",
    description="AI Resume Analyzer using RAG",
    version="1.0.0",
)


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# CORS
# ============================================================

ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    "http://localhost:8000",
    "http://127.0.0.1:8000",

    # Docker frontend
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# FRONTEND
# ============================================================

FRONTEND_DIR = BASE_DIR / "frontend"

if FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(
            directory=str(FRONTEND_DIR)
        ),
        name="static",
    )


# ============================================================
# GLOBAL VARIABLES
# ============================================================

vector_store = None
retriever = None
rag_chain = None

resume_text = ""
resume_filename = ""


# ============================================================
# REQUEST MODELS
# ============================================================

class QuestionRequest(BaseModel):
    question: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def serve_frontend():
    """
    Serve frontend index.html.
    """

    index_path = FRONTEND_DIR / "index.html"

    if index_path.exists():
        return FileResponse(
            index_path
        )

    return {
        "message": "Frontend is not available."
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    """
    Health check.
    """

    return {
        "status": "ok",
        "backend": "running",
        "rag_ready": rag_chain is not None,
    }


# ============================================================
# API STATUS
# ============================================================

@app.get("/api/status")
def api_status():

    return {
        "status": "connected",
        "backend": "FastAPI",
        "rag_ready": rag_chain is not None,
        "resume_uploaded": bool(resume_text),
    }


# ============================================================
# MODELS
# ============================================================

@app.get("/models")
def list_models():

    return {
        "chat_model": GROQ_LLM_MODEL_NAME,
        "embedding_model": "TF-IDF",
    }


# ============================================================
# GROQ ASYNC FUNCTION
# ============================================================

async def call_groq(prompt: str) -> str:
    """
    Run synchronous Groq SDK inside a worker thread.

    This prevents the FastAPI event loop from being blocked.
    """

    try:

        response = await asyncio.to_thread(
            client.chat.completions.create,

            model=GROQ_LLM_MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI resume analyzer. "
                        "Analyze resumes accurately and professionally. "
                        "Use only information present in the resume "
                        "when answering resume-specific questions."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0.2,
            max_tokens=3000,
        )

        if not response.choices:
            raise RuntimeError(
                "Groq returned no response."
            )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError(
                "Groq returned an empty response."
            )

        return answer.strip()

    except Exception as e:

        print("=" * 60)
        print("GROQ ERROR")
        print(type(e).__name__)
        print(str(e))
        print("=" * 60)

        raise


# ============================================================
# RESUME ANALYSIS
# ============================================================

async def make_resume_analysis(
    text: str
) -> str:

    prompt = f"""
You are an expert professional resume analyzer.

Analyze the following resume.

Provide a clear professional analysis containing:

1. Overall Resume Summary
2. Technical Skills
3. Programming Languages
4. Frameworks and Libraries
5. Tools and Technologies
6. Projects
7. Education
8. Experience
9. Strengths
10. Weaknesses
11. Missing Skills
12. ATS Suggestions
13. Resume Improvement Suggestions
14. Suitable Job Roles

Use ONLY information available in the resume.

Do not invent qualifications or experience.

Resume:

{text}
"""

    return await call_groq(
        prompt
    )


# ============================================================
# UPLOAD RESUME
# ============================================================

@app.post("/upload")
async def upload_resume(
    file: UploadFile = File(...)
):

    global vector_store
    global retriever
    global rag_chain
    global resume_text
    global resume_filename

    try:

        # ----------------------------------------------------
        # Validate filename
        # ----------------------------------------------------

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="No file selected."
            )

        filename = Path(
            file.filename
        ).name

        # ----------------------------------------------------
        # Validate PDF
        # ----------------------------------------------------

        if not filename.lower().endswith(".pdf"):

            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # ----------------------------------------------------
        # Ensure upload directory
        # ----------------------------------------------------

        UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = UPLOAD_DIR / filename

        # ----------------------------------------------------
        # Save uploaded file
        # ----------------------------------------------------

        file_content = await file.read()

        await asyncio.to_thread(
            file_path.write_bytes,
            file_content
        )

        print("=" * 60)
        print("PDF UPLOAD")
        print("Filename:", filename)
        print("Path:", file_path)
        print("=" * 60)

        # ----------------------------------------------------
        # LOAD PDF
        #
        # Heavy synchronous operation moved to thread.
        # ----------------------------------------------------

        print("Loading PDF...")

        documents = await asyncio.to_thread(
            load_pdf,
            str(file_path)
        )

        if not documents:

            raise HTTPException(
                status_code=400,
                detail="No text found in PDF."
            )

        print(
            "Documents loaded:",
            len(documents)
        )

        # ----------------------------------------------------
        # Extract text
        # ----------------------------------------------------

        extracted_parts = []

        for doc in documents:

            try:

                if hasattr(
                    doc,
                    "page_content"
                ):

                    content = doc.page_content

                elif hasattr(
                    doc,
                    "text"
                ):

                    content = doc.text

                else:

                    content = str(doc)

                if content:

                    extracted_parts.append(
                        str(content)
                    )

            except Exception:
                continue

        resume_text = "\n\n".join(
            extracted_parts
        ).strip()

        if not resume_text:

            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF."
            )

        resume_filename = filename

        print(
            "Extracted characters:",
            len(resume_text)
        )

        # ----------------------------------------------------
        # SPLIT DOCUMENTS
        # ----------------------------------------------------

        print("Creating chunks...")

        chunks = await asyncio.to_thread(
            split_documents,
            documents
        )

        if not chunks:

            raise HTTPException(
                status_code=400,
                detail="Could not create text chunks from PDF."
            )

        print(
            "Chunks created:",
            len(chunks)
        )

        # ----------------------------------------------------
        # CREATE VECTOR STORE
        # ----------------------------------------------------

        print("Creating vector store...")

        vector_store = await asyncio.to_thread(
            create_vector_store,
            chunks
        )

        print(
            "Vector store created."
        )

        # ----------------------------------------------------
        # CREATE RETRIEVER
        # ----------------------------------------------------

        print("Creating retriever...")

        retriever = await asyncio.to_thread(
            get_retriever,
            vector_store
        )

        print(
            "Retriever created."
        )

        # ----------------------------------------------------
        # CREATE RAG CHAIN
        # ----------------------------------------------------

        print("Creating RAG chain...")

        rag_chain = await asyncio.to_thread(
            create_rag_chain,
            retriever
        )

        print(
            "RAG chain created."
        )

        # ----------------------------------------------------
        # AI RESUME ANALYSIS
        # ----------------------------------------------------

        print("Analyzing resume with Groq...")

        analysis = await make_resume_analysis(
            resume_text
        )

        print(
            "Resume analysis completed."
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "message":
                "Resume uploaded successfully",

            "filename":
                filename,

            "chunks_created":
                len(chunks),

            "analysis":
                analysis,

            "status":
                "success",
        }

    except HTTPException:
        raise

    except Exception as e:

        print("=" * 60)
        print("UPLOAD ERROR")
        print(type(e).__name__)
        print(str(e))
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# ASK RESUME QUESTION
# ============================================================

async def answer_resume_question(
    question: str,
    context: str
) -> str:

    prompt = f"""
You are an AI assistant that answers questions
about a user's uploaded resume.

Use ONLY the provided resume context.

If the answer cannot be found in the resume,
clearly say that the information is not available
in the uploaded resume.

Do not invent information.

Resume Context:
----------------
{context}
----------------

Question:
{question}

Give a clear and useful answer.
"""

    return await call_groq(
        prompt
    )


# ============================================================
# ASK ENDPOINT
# ============================================================

@app.post("/ask")
async def ask_resume(
    request: QuestionRequest
):

    global retriever
    global rag_chain

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # --------------------------------------------------------
    # Make sure resume exists
    # --------------------------------------------------------

    if retriever is None and rag_chain is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please upload a resume "
                "before asking questions."
            )
        )

    try:

        context = ""

        # ----------------------------------------------------
        # Preferred: Retriever
        # ----------------------------------------------------

        if retriever is not None:

            try:

                if hasattr(
                    retriever,
                    "invoke"
                ):

                    docs = await asyncio.to_thread(
                        retriever.invoke,
                        question
                    )

                else:

                    docs = await asyncio.to_thread(
                        retriever.get_relevant_documents,
                        question
                    )

                context_parts = []

                for doc in docs:

                    if hasattr(
                        doc,
                        "page_content"
                    ):

                        context_parts.append(
                            doc.page_content
                        )

                    else:

                        context_parts.append(
                            str(doc)
                        )

                context = "\n\n".join(
                    context_parts
                )

            except Exception as e:

                print(
                    "Retriever warning:",
                    str(e)
                )

        # ----------------------------------------------------
        # Fallback to complete resume text
        # ----------------------------------------------------

        if not context:

            context = resume_text

        if not context:

            raise HTTPException(
                status_code=400,
                detail="Resume content is unavailable."
            )

        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        answer = await answer_resume_question(
            question,
            context
        )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return {
            "question":
                question,

            "answer":
                answer,

            "status":
                "success",
        }

    except HTTPException:
        raise

    except Exception as e:

        print("=" * 60)
        print("ASK ERROR")
        print(type(e).__name__)
        print(str(e))
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# CLEAR RESUME
# ============================================================

@app.post("/clear")
async def clear_resume():

    global vector_store
    global retriever
    global rag_chain
    global resume_text
    global resume_filename

    vector_store = None
    retriever = None
    rag_chain = None
    resume_text = ""
    resume_filename = ""

    return {
        "message":
            "Resume data cleared.",
        "status":
            "success",
    }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():

    print("=" * 60)
    print("AI RESUME RAG ASSISTANT")
    print("=" * 60)
    print("Backend started successfully.")
    print(
        "Groq model:",
        GROQ_LLM_MODEL_NAME
    )
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )