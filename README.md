# SMARTTOEFL AI

SMARTTOEFL AI is a local TOEFL practice application with a FastAPI backend, a Vue 3 frontend, SQLite history tracking, RAG-based TOEFL material retrieval, and local LLM responses through Ollama.

## Features

- Generate TOEFL-style questions by category and difficulty.
- Evaluate answers with bilingual English/Indonesian feedback.
- Store practice history in SQLite.
- Show analytics, weakness analysis, and recommendations.
- Use local TOEFL material from `backend/app/dataset` with Chroma vector search.
- Run with a local Ollama model, so no external LLM API key is required.

## Project Structure

```text
.
+-- backend/
|   +-- app/
|   |   +-- api/routes/          # FastAPI endpoints
|   |   +-- core/database.py     # SQLite configuration
|   |   +-- dataset/             # TOEFL source material
|   |   +-- models/              # SQLAlchemy models
|   |   +-- services/            # LLM and RAG services
|   +-- build_rag.py             # Builds the Chroma vectorstore
|   +-- requirements.txt         # Python dependencies
+-- frontend/
    +-- ui/
        +-- src/                 # Vue app source
        +-- package.json         # Node dependencies and scripts
        +-- .env.example         # Frontend environment template
```

## Requirements

- Python 3.10 or newer.
- Node.js 20 or newer.
- Ollama installed locally.
- Internet connection for first-time Python package install and first-time model/embedding downloads.

The backend currently uses this Ollama model:

```text
qwen2.5:1.5b
```

## Backend Setup

Open a terminal in the backend folder:

```powershell
cd backend
```

Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install and prepare the Ollama model:

```powershell
ollama pull qwen2.5:1.5b
```

Make sure the Ollama app/service is running before using AI endpoints.

Build the RAG vectorstore:

```powershell
python build_rag.py
```

Run the API:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check the backend:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{"message":"SMARTTOEFL AI Backend Running"}
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open a second terminal in the frontend app folder:

```powershell
cd frontend\ui
```

Install dependencies:

```powershell
npm install
```

Create the frontend env file:

```powershell
copy .env.example .env
```

The default API URL is:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Run the frontend:

```powershell
npm run dev
```

Open the Vite URL shown in the terminal, usually:

```text
http://127.0.0.1:5173/
```

## Common Workflow

1. Start Ollama.
2. Start the backend with `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
3. Start the frontend with `npm run dev`.
4. Open the frontend in your browser.

## Backend Endpoints

- `GET /` - health check.
- `POST /generate-question` - generate a TOEFL question.
- `POST /evaluate-answer` - evaluate a submitted answer and save history.
- `GET /analytics` - practice statistics.
- `GET /history` - practice history.
- `DELETE /history` - clear practice history.
- `GET /recommendation` - study recommendation.
- `GET /weakness-analysis` - weakness score summary.

## Generated Files

These files/folders are generated locally and are intentionally ignored by Git:

- `backend/venv/`
- `backend/smarttoefl.db`
- `backend/app/vectorstore/`
- `frontend/ui/node_modules/`
- `.env` files

If the vectorstore is missing, rerun:

```powershell
cd backend
venv\Scripts\activate
python build_rag.py
```

If the database is missing, it will be created automatically when the backend starts.

## Troubleshooting

### `ModuleNotFoundError: No module named 'fastapi'`

You are missing backend dependencies or using the wrong Python environment.

```powershell
cd backend
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### `ModuleNotFoundError: No module named 'langchain_core.schema'`

Use the current import:

```python
from langchain_core.documents import Document
```

### Ollama errors

Make sure Ollama is installed, running, and the model exists locally:

```powershell
ollama list
ollama pull qwen2.5:1.5b
```

### Frontend cannot connect to backend

Check that the backend is running on port `8000` and that `frontend/ui/.env` contains:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Restart `npm run dev` after changing `.env`.

## Useful Commands

Build frontend for production:

```powershell
cd frontend\ui
npm run build
```

Preview production build:

```powershell
npm run preview
```

Rebuild backend vectorstore:

```powershell
cd backend
venv\Scripts\activate
python build_rag.py
```
