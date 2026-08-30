import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# ENVIRONMENT
# ============================================================

# First try backend/.env
BACKEND_ENV = BASE_DIR / ".env"

# Then try project-root .env
ROOT_ENV = BASE_DIR.parent / ".env"

if BACKEND_ENV.exists():
    load_dotenv(BACKEND_ENV, override=False)

if ROOT_ENV.exists():
    load_dotenv(ROOT_ENV, override=False)


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_LLM_MODEL_NAME = os.getenv(
    "GROQ_LLM_MODEL_NAME",
    "openai/gpt-oss-20b"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2"
)


# Keep this alias because some files may import EMBEDDING_MODEL
EMBEDDING_MODEL = EMBEDDING_MODEL_NAME


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# VECTOR STORE DIRECTORY
# ============================================================

VECTOR_DB_DIR = BASE_DIR / "vector_db"
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# TEXT CHUNKING
# ============================================================

CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", "1000")
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", "200")
)


# ============================================================
# VALIDATION
# ============================================================

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. "
        "Add GROQ_API_KEY to your .env file."
    )


# ============================================================
# CONFIG LOG
# ============================================================

print("=" * 60)
print("CONFIGURATION LOADED")
print("=" * 60)
print(f"BASE_DIR              : {BASE_DIR}")
print(f"GROQ API key          : Loaded")
print(f"GROQ model            : {GROQ_LLM_MODEL_NAME}")
print(f"Embedding model       : {EMBEDDING_MODEL_NAME}")
print(f"Upload directory      : {UPLOAD_DIR}")
print(f"Vector DB directory    : {VECTOR_DB_DIR}")
print(f"Chunk size            : {CHUNK_SIZE}")
print(f"Chunk overlap         : {CHUNK_OVERLAP}")
print("=" * 60)