# AUTOSAR AI — Execution & Run Instructions

## 1. Prerequisites Check
1. **Python 3.11+**: Verify Python installation:
   ```powershell
   python --version
   ```
2. **Local Ollama**: Ensure Ollama is installed and the `llama3.2:3b` model is downloaded:
   ```powershell
   ollama list
   # If llama3.2:3b is not present, pull it:
   ollama pull llama3.2:3b
   ```
   Start the Ollama server:
   ```powershell
   ollama serve
   ```

## 2. Environment Setup
1. Open PowerShell and navigate to the `Code` directory:
   ```powershell
   cd SASTRA_HamdhanAhmedB_127003081_CSx_AIML\Code
   ```
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .env\Scripts\Activate.ps1
   ```
3. Install required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Configure environment settings:
   ```powershell
   Copy-Item .env.example .env
   ```

## 3. Starting the Services

### Option A: Unified Launcher
Run both FastAPI backend and Streamlit frontend using the provided runner:
```powershell
python run.py
```

### Option B: Dual Terminal Execution (Recommended for Debugging)

**Terminal 1 — FastAPI Backend:**
```powershell
.env\Scripts\Activate.ps1
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Health Endpoint: `http://localhost:8000/health`
- Interactive API Swagger Docs: `http://localhost:8000/docs`

**Terminal 2 — Streamlit Frontend:**
```powershell
.env\Scripts\Activate.ps1
python -m streamlit run frontend/app.py --server.port 8501
```
- Web Application URL: `http://localhost:8501`

## 4. Running the Automated Test Suite
To verify the complete test suite (28 automated tests across 12 modules):
```powershell
python -m pytest tests/ -v
```
Expected Result: `28 passed in ~27s` (100% pass rate).
