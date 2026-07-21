import os
from pathlib import Path
from dotenv import load_dotenv

# Define base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing! Please set it in your .env file."
    )

# Models Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_LLM_MODEL_NAME = "llama-3.1-8b-instant"

# Storage Directories
UPLOAD_DIR = BASE_DIR / "uploads"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

# Create directories safely
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# Chunking Parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200