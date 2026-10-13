# AUTOSAR AI — Comprehensive Implementation & Architecture Audit

## 1. Executive Summary
The **AUTOSAR AI — High-Level Design (HLD) Document Intelligence Platform** is an enterprise-grade engineering intelligence application designed to ingest automotive specification documents (AUTOSAR HLD, SRS, ICD), extract architectural entities, analyze component dependencies, enforce enterprise compliance rules, calculate structural diffs across specification revisions, and provide grounded retrieval-augmented intelligence (RAG) powered by a local Ollama Large Language Model (`llama3.2:3b`).

---

## 2. Real Technology Stack

| Layer | Technologies & Libraries | Version / Notes |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit, Streamlit Custom Components, Vanilla CSS | `streamlit>=1.32.0`, Custom CSS Design System |
| **Backend API** | FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings | `fastapi>=0.110.0`, `uvicorn>=0.27.1` |
| **Relational Database** | SQLite, SQLAlchemy 2.0 ORM, Alembic | SQLite with Thread-Safe Connection Pooling |
| **Vector Database** | ChromaDB (Persistent Disk Store) | `chromadb>=0.4.24`, Persistent directory: `./data/vector_store` |
| **Document Processing** | PyMuPDF (fitz) | `PyMuPDF>=1.23.26` (high-fidelity PDF text & page extraction) |
| **Local LLM Engine** | Ollama, Model: `llama3.2:3b` | Local HTTP API at `http://localhost:11434`, Storage at `H:\OllamaModels` |
| **Hosted LLM (Optional)** | Google Gemini Generative AI | `google-generativeai>=0.4.1` (Optional fallback if chosen) |
| **Automated Testing** | Pytest, FastAPI TestClient, Requests | `pytest>=8.0.2`, `httpx>=0.27.0` |

---

## 3. Directory Structure & Key Files

```
h:\tech_pulse_project\autosar-ai\
├── .env                       # Environment configuration (LLM, DB, chunking parameters)
├── requirements.txt           # Project dependencies
├── run.py                     # Unified startup script (launches FastAPI on :8000 & Streamlit on :8501)
├── backend/
│   ├── main.py                # FastAPI application entry point, CORS, and route registration
│   ├── core/
│   │   └── config.py          # Pydantic BaseSettings loading .env configuration
│   ├── database/
│   │   ├── base.py            # SQLAlchemy declarative base
│   │   └── connection.py      # Engine and SessionLocal factory
│   ├── models/
│   │   └── domain.py          # Data models: Project, Document, Chunk, Entity, Finding, Comparison, Report
│   ├── schemas/
│   │   └── domain.py          # Pydantic schemas for requests & responses
│   ├── services/
│   │   ├── document_service.py   # PyMuPDF extraction, chunking, entity extraction, and rule validation
│   │   ├── llm_service.py        # Local Ollama provider abstraction, diagnostics, and grounded prompting
│   │   └── vector_store_service.py # ChromaDB collection management, chunk indexing, search, deletion
│   └── api/v1/
│       ├── projects.py        # Project CRUD & dashboard metrics
│       ├── documents.py       # PDF upload, status polling, reprocess, and delete
│       ├── sessions.py        # AI Assistant /ask endpoint and session history
│       ├── entities.py        # Architecture entity inspection and review status
│       ├── comparisons.py     # Document comparison calculation and history
│       ├── findings.py        # Architecture findings list, update, and review
│       ├── reports.py         # Architecture & Findings report generation and secure download
│       ├── settings.py        # Parameter persistence & validation
│       └── diagnostics.py     # Subsystem health verification (FastAPI, SQLite, ChromaDB, Ollama)
├── frontend/
│   ├── app.py                 # Streamlit entry point and landing page
│   ├── utils/
│   │   └── ui.py              # Custom CSS theme (White & Blue SaaS design system)
│   └── pages/
│       ├── 1_Dashboard.py     # Project metrics, recent documents, system diagnostics
│       ├── 2_Documents.py     # Document repository, inspection, upload, reprocess, delete
│       ├── 3_Architecture_Explorer.py # Entity inspection, filtering, review confirmation
│       ├── 4_AI_Assistant.py  # Grounded RAG chat, document scoping, suggested questions, citations
│       ├── 5_Comparisons.py   # Document Comparison & Comparison History tabs
│       ├── 6_Findings.py      # Severity/status filters, issue review, and persistence
│       ├── 7_Reports.py       # CSV, JSON, and PDF report generation and download
│       └── 8_Settings.py      # Extraction sliders, enterprise rule checkboxes, persistence
├── data/
│   ├── autosar_ai.db          # SQLite persistent database
│   ├── uploads/               # Uploaded PDF document storage
│   ├── exports/               # Generated reports and exports
│   ├── settings.json          # Persisted extraction & rule configuration
│   └── vector_store/          # ChromaDB persistent vector index
├── docs/                      # Architectural, setup, user, and verification documentation
└── tests/                     # Pytest automated test suite
```

---

## 4. Known Defects Identified & Completed Repairs

| Defect # | Category | Description | Root Cause | Fix Applied | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEF-001** | Navigation | Duplicate sidebar navigation entries (`Comparison` and `Comparisons`) | Redundant file `5_Comparison.py` alongside `5_Comparisons.py` | Removed duplicate file; canonicalized `5_Comparisons.py` with tabs for "Document Comparison" and "Comparison History". | **FIXED** |
| **DEF-002** | Frontend CSS | Blank outlined rounded containers appearing across multiple pages | Global CSS selector `div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"]` matching all Streamlit column wrappers | Refined selector to target only `[data-testid="stMetric"]` and explicit `.card` containers. | **FIXED** |
| **DEF-003** | AI Integration | LLM Provider hardcoded to `llama2` instead of installed `llama3.2:3b` | `config.py` default was `llama2`, missing unified provider abstraction | Updated `backend/core/config.py` and `.env` to `llama3.2:3b` with clean provider abstraction in `llm_service.py`. | **FIXED** |
| **DEF-004** | Document Pipeline | Document ingestion pipeline was a simulated mock with `time.sleep(2)` | Placeholder code in `document_service.py` | Implemented full PyMuPDF extraction, page tracking, chunk hashing, ChromaDB indexing, entity extraction, and rule validation. | **FIXED** |
| **DEF-005** | AI Assistant | Chat queries lacked source citations and clicked suggested questions did nothing | Missing citation serialization and static HTML list in UI | Enriched `/ask` endpoint with source documents, pages, excerpts; made suggested questions interactive buttons. | **FIXED** |
| **DEF-006** | Comparisons | Comparisons returned empty hardcoded JSON; history was unretrievable | Stubbed `results_json` and missing GET history endpoint | Implemented real entity diffing (added, removed, modified) and `GET /projects/{id}/comparisons` history route. | **FIXED** |
| **DEF-007** | Findings | Static dummy table with non-functional HTML "Review" buttons | `6_Findings.py` contained hardcoded HTML markup | Wired page to `GET /api/v1/projects/{id}/findings` with interactive status/comment review and SQLite persistence. | **FIXED** |
| **DEF-008** | Reports & Exports | Mock 2-line text file generation with non-functional download links | Static HTML table and stubbed file write | Implemented real CSV and JSON export from live database, added CSV spreadsheet formula sanitization, and real `st.download_button`. | **FIXED** |
| **DEF-009** | Settings | Sliders and checkboxes did not persist values across restarts | No persistence backend for UI controls | Implemented `/api/v1/settings` endpoint persisting configuration to `data/settings.json` and validating `overlap < chunk_size`. | **FIXED** |
| **DEF-010** | Diagnostics | Diagnostics was a simple ping without model verification | Missing subsystem health verification | Built `/api/v1/diagnostics` executing real checks on FastAPI, SQLite, ChromaDB, Ollama `llama3.2:3b` generation, and PyMuPDF. | **FIXED** |

---

## 5. Startup Commands

### Run Both Services via Unified Launcher
```powershell
.\venv\Scripts\python run.py
```

### Run Backend API Separately
```powershell
.\venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Frontend Streamlit Separately
```powershell
.\venv\Scripts\python -m streamlit run frontend/app.py --server.port 8501
```

### Run Full Pytest Suite
```powershell
.\venv\Scripts\python -m pytest tests/ -v
```
