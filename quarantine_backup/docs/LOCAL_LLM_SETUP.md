# Local Ollama LLM Configuration & Verification Guide

## 1. Overview
The AUTOSAR AI platform is pre-configured for **100% offline, privacy-preserving local AI inference** using **Ollama** with the **`llama3.2:3b`** model. Proprietary automotive engineering designs, software component architectures, and interface definitions never leave your local machine or traverse external networks.

---

## 2. Verified Local Setup

| Parameter | Configured Value | Status |
| :--- | :--- | :--- |
| **Ollama Binary Version** | `0.40.3` | **VERIFIED** |
| **Active Model** | `llama3.2:3b` (ID: `a80c4f17acd5`, 2.0 GB) | **INSTALLED & VERIFIED** |
| **Model Storage Location** | `H:\OllamaModels` | **CONFIGURED** |
| **Local Service Endpoint** | `http://localhost:11434` | **ONLINE** |
| **Generation Latency** | ~3–8 seconds (3B parameters) | **TESTED** |
| **Local Embedding Model** | `all-MiniLM-L6-v2` (SentenceTransformers) | **LOCAL & VERIFIED** |

---

## 3. Configuration in `.env`
The `.env` file in the project root (`h:\tech_pulse_project\autosar-ai\.env`) is set to:

```ini
# LLM Provider Configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:3b
LLM_BASE_URL=http://localhost:11434
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Embedding Engine Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K=5
SIMILARITY_THRESHOLD=0.5
```

> [!NOTE]
> No API key is required when `LLM_PROVIDER=ollama`. The platform will **never** silently fall back to Gemini or any hosted cloud service if local mode is selected.

---

## 4. Verification & Diagnostic Commands

### 4.1 Check Ollama Version and Installed Models
Run in PowerShell:
```powershell
ollama --version
ollama list
```
Expected output:
```
ollama version is 0.40.3
NAME           ID              SIZE      MODIFIED
llama3.2:3b    a80c4f17acd5    2.0 GB    ...
```

### 4.2 Query the Local HTTP API
```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

### 4.3 Test Direct Local Generation
```powershell
$body = @{ 
    model = "llama3.2:3b"
    prompt = "Respond in 3 words: Diagnostic confirmed OK."
    stream = $false 
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
```

### 4.4 Automated Application Diagnostics
Run the diagnostic suite embedded in the application:
```powershell
.\venv\Scripts\python -c "from backend.services.llm_service import test_llm_connection; import json; print(json.dumps(test_llm_connection(), indent=2))"
```
Expected output:
```json
{
  "status": "PASS",
  "provider": "ollama",
  "model": "llama3.2:3b",
  "reachable": true,
  "model_exists": true,
  "test_generation_ok": true,
  "response_sample": "...",
  "latency_ms": 7800.0,
  "error_message": null
}
```

---

## 5. Privacy & Data Isolation Guarantees

1. **No External Network Egress**: Prompts, chunk text, and architectural entity excerpts are delivered strictly to `http://localhost:11434/api/generate`.
2. **Local Embeddings**: Embeddings are computed locally on your CPU/GPU using the HuggingFace `all-MiniLM-L6-v2` transformer model and stored in `./data/vector_store/` via ChromaDB.
3. **No Silent Cloud Fallback**: If Ollama is offline, the application returns a clear diagnostic error instructing you to launch Ollama. It does not redirect proprietary specifications to external cloud APIs.
4. **Project-Level Isolation**: Document chunks and vector embeddings are segregated by `project_id` in ChromaDB collections (`project_{id}`) and SQLite tables.

---

## 6. Troubleshooting

| Symptom | Probable Cause | Action |
| :--- | :--- | :--- |
| `Cannot connect to Ollama at http://localhost:11434` | The Ollama service is stopped | Launch the Ollama Windows application from the Start Menu or run `ollama serve` in a terminal. |
| `Model 'llama3.2:3b' not found in Ollama` | Model deleted or storage path changed | Run `ollama pull llama3.2:3b`. Verify `OLLAMA_MODELS` environment variable points to `H:\OllamaModels`. |
| Generation timed out after 120s | System under heavy RAM/GPU load | Close background memory-heavy apps. The timeout in `backend/services/llm_service.py` is configured to 120 seconds. |
| Port 11434 already in use | Another Ollama process is running | Normal. The running service handles requests directly. |
