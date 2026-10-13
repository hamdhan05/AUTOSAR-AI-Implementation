# AUTOSAR AI — Source Code Directory

## 1. Directory Structure
```
Code/
├── backend/                  # FastAPI Application, REST Routers, Services & Database Models
│   ├── api/v1/               # API endpoint routers (documents, sessions, entities, comparisons, etc.)
│   ├── core/                 # App configuration and Pydantic settings
│   ├── database/             # SQLAlchemy engine, session maker, Base models
│   ├── models/               # Domain ORM models (14 tables)
│   ├── schemas/              # Pydantic request/response schemas
│   └── services/             # Core business logic:
│       ├── document_service.py      # PyMuPDF extraction, chunking, heuristic entity regex
│       ├── vector_store_service.py  # Persistent ChromaDB client and collection management
│       ├── retrieval_service.py     # Dense search + BM25 keyword search with Reciprocal Rank Fusion
│       ├── llm_service.py           # Local Ollama client (llama3.2:3b) & Grounded prompt
│       ├── grounding_service.py     # Claim decomposition & Grounding Score validation
│       ├── graph_service.py         # Architecture dependency & Mermaid diagram generation
│       ├── report_generator.py      # CSV export with formula injection sanitization
│       └── evaluation_service.py    # 35-query benchmark evaluation engine
├── frontend/                 # Streamlit Multi-Page Web Application
│   ├── app.py                # Main application entry point & navigation
│   ├── pages/                # 9 interactive frontend pages:
│   │   ├── 1_Dashboard.py            # Overview, project statistics, quick action cards
│   │   ├── 2_Documents.py            # PDF upload, ingestion status, document governance
│   │   ├── 3_Architecture_Explorer.py# Extracted entities, ports/signals table, Mermaid graphs
│   │   ├── 4_AI_Assistant.py         # Grounded RAG query interface, citations, claim verification
│   │   ├── 5_Comparisons.py          # HLD revision diff, entity delta, rename detection
│   │   ├── 6_Findings.py             # Rule-based architectural findings & reviewer workflow
│   │   ├── 7_Reports.py              # Export audit reports & CSV downloads
│   │   ├── 8_Settings.py             # System parameters, chunk size/overlap, diagnostics
│   │   └── 9_Evaluation.py           # Benchmark execution & evaluation metrics display
│   ├── components/           # Reusable UI widgets and custom layout cards
│   ├── services/             # Frontend API client communicating with backend
│   └── utils/                # Styling and formatting helpers
├── tests/                    # Automated Pytest Test Suite (28 passing tests)
│   ├── conftest.py           # Shared test fixtures and test database sessions
│   └── unit/                 # 12 test modules covering all subsystems
├── alembic.ini               # Database migration configuration
├── requirements.txt          # Python dependency specifications
├── .env.example              # Environment variables template
├── run.py                    # Dual-process launcher for FastAPI and Streamlit
└── run_instructions.md       # Step-by-step terminal commands for running the app
```

## 2. Dependencies & Runtime Prerequisites
- Python 3.11.x (tested on Python 3.11.9)
- Local Ollama runtime with `llama3.2:3b` model
- Chrome / Edge / Firefox browser for the Streamlit UI

Refer to `run_instructions.md` for complete installation and startup instructions.
