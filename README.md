# 🤖 RAG AI Resume Analyzer

> 🚀 An AI-powered Resume Analyzer built with **FastAPI, LangChain, FAISS, HuggingFace Embeddings, and Groq LLM** using Retrieval-Augmented Generation (RAG).

---

## ✨ Features

- 📄 Upload Resume (PDF)
- 🤖 AI Resume Analysis
- 🔍 Semantic Search with FAISS
- 🧠 HuggingFace Embeddings
- ⚡ FastAPI REST API
- 🌐 Responsive Frontend
- 💡 Resume Improvement Suggestions
- 🎯 Career Insights
- ☁️ Easy Deployment (Render & Vercel)

---

## 🏗️ Architecture

```text
          📄 Resume
               │
               ▼
      📖 Document Loader
               │
               ▼
       ✂️ Text Splitter
               │
               ▼
   🧠 HuggingFace Embeddings
               │
               ▼
      🗂️ FAISS Vector Store
               │
               ▼
        🔍 RAG Retriever
               │
               ▼
         🤖 Groq LLM
               │
               ▼
      📊 AI Resume Analysis
```

---

## 📂 Project Structure

```text
📦 RAG_AI_Resume_Analyzer
│
├── 📁 backend
│   ├── app.py
│   ├── config.py
│   ├── document_loader.py
│   ├── embeddings.py
│   ├── rag_chain.py
│   ├── resume_analyzer.py
│   ├── text_splitter.py
│   ├── vector_store.py
│   └── requirements.txt
│
├── 📁 frontend
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── 📄 README.md
```

---

## 🛠️ Tech Stack

| 🚀 Technology | 💡 Usage |
|--------------|----------|
| 🐍 Python | Backend |
| ⚡ FastAPI | REST API |
| 🦜 LangChain | RAG Pipeline |
| 🤗 HuggingFace | Embeddings |
| 🗂️ FAISS | Vector Database |
| 🤖 Groq | LLM |
| 🌐 HTML | Frontend |
| 🎨 CSS | Styling |
| ⚡ JavaScript | Client Side |

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/SubbaReddy-AI/RAG-AI_Resume_Analyzer.git
cd RAG-AI_Resume_Analyzer
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4️⃣ Add Environment Variable

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

### 5️⃣ Run the Backend

```bash
uvicorn backend.app:app --reload
```

Open:

```
http://127.0.0.1:8000
```

---

## 🔄 Workflow

```text
📄 Upload Resume
       │
       ▼
📖 Extract Text
       │
       ▼
✂️ Split into Chunks
       │
       ▼
🧠 Generate Embeddings
       │
       ▼
🗂️ Store in FAISS
       │
       ▼
🔍 Retrieve Relevant Context
       │
       ▼
🤖 Groq LLM
       │
       ▼
📊 Resume Analysis
```

---

## 📡 API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Analyze uploaded resume |

---

## 🚀 Future Improvements

- ✅ ATS Score Checker
- ✅ Resume Ranking
- ✅ Job Recommendation
- ✅ Interview Questions
- ✅ Resume Chatbot
- ✅ PDF Report Export

---


---

## 👨‍💻 Author

**Yakkanti Subba Reddy**

🎓 B.Tech – Computer Science & Engineering (AI & ML)

💻 AI • Machine Learning • NLP • Generative AI

⭐ If you found this project useful, don't forget to **Star ⭐ the repository!**

---

## 📜 License

This project is licensed under the **MIT License**.
