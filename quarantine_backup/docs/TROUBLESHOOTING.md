# AUTOSAR AI — Comprehensive Troubleshooting Guide

This guide provides fast, actionable solutions for common issues across the application, database, vector store, and local Ollama model.

---

## 1. Startup & Environment Issues

### ❌ `ModuleNotFoundError: No module named 'fastapi'` (or other package)
- **Root Cause**: Command executed using global Python rather than the project virtual environment.
- **Solution**: Execute commands using the venv python interpreter:
  ```powershell
  .\venv\Scripts\python run.py
  ```

### ❌ `ModuleNotFoundError: No module named 'backend'` when running pytest
- **Root Cause**: Direct `pytest` invocation does not automatically inject the workspace root into `sys.path`.
- **Solution**: Use the module runner:
  ```powershell
  .\venv\Scripts\python -m pytest tests/
  ```

### ❌ Port 8000 or 8501 Already in Use
- **Root Cause**: An existing instance of FastAPI or Streamlit is already running.
- **Solution**: Identify and terminate the lingering process:
  ```powershell
  Get-Process -Name python | Where-Object { $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*streamlit*" } | Stop-Process -Force
  ```

---

## 2. Local Ollama & AI Issues

### ❌ `Cannot connect to Ollama at http://localhost:11434`
- **Root Cause**: The Ollama background service is not running.
- **Solution**:
  1. Open the Windows Start Menu and launch **Ollama**.
  2. Or start it manually in a terminal:
     ```powershell
     ollama serve
     ```
  3. Verify reachability:
     ```powershell
     Invoke-RestMethod http://localhost:11434/api/tags
     ```

### ❌ `Model 'llama3.2:3b' not found in Ollama`
- **Root Cause**: The model tag is missing from Ollama's configured model directory (`H:\OllamaModels`).
- **Solution**:
  1. Verify installed models:
     ```powershell
     ollama list
     ```
  2. If missing, pull the exact 3B model:
     ```powershell
     ollama pull llama3.2:3b
     ```

### ❌ AI Assistant Generation Times Out (120s)
- **Root Cause**: Workstation under heavy memory or CPU/GPU load while processing long document contexts.
- **Solution**:
  1. Reduce chunk size or select a specific document in **"Scope Analysis"** instead of querying across all documents.
  2. Check task manager memory utilization.

---

## 3. Document Processing & Ingestion

### ❌ `File exceeds maximum upload limit of 50MB` (`413 Payload Too Large`)
- **Root Cause**: Uploaded file exceeds the configured limit in `.env` (`MAX_UPLOAD_MB=50`).
- **Solution**: Increase `MAX_UPLOAD_MB` in `.env` if necessary for large automotive specifications.

### ❌ Document Stays in `PROCESSING` State
- **Root Cause**: Unhandled exception during extraction or corrupted PDF stream.
- **Solution**:
  1. Check document status:
     ```powershell
     Invoke-RestMethod http://127.0.0.1:8000/api/v1/documents/{document_id}/status
     ```
  2. Click **"🔄 Reprocess"** on the Documents page.

---

## 4. Vector Store & Database

### ❌ ChromaDB Locking or Persistence Errors
- **Root Cause**: Corrupted vector index in `./data/vector_store`.
- **Solution**: If vector index becomes corrupted during an abrupt system termination:
  1. Stop both backend and frontend services.
  2. Delete the `./data/vector_store` folder.
  3. Restart the backend; ChromaDB will automatically re-create the persistent client directory.
  4. Click **"🔄 Reprocess"** on documents to re-index chunks.

### ❌ SQLite `database is locked`
- **Root Cause**: Concurrent uncommitted write operations.
- **Solution**: The application uses `SessionLocal()` with connection pooling and `check_same_thread=False`. Ensure no external SQLite browsing tools have an uncommitted transaction open on `data/autosar_ai.db`.
