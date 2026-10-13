# AUTOSAR AI — Comprehensive Testing & Quality Assurance Guide

## 1. Overview
The AUTOSAR AI test suite validates backend API endpoints, SQLite persistence, ChromaDB vector indexing, PyMuPDF extraction, enterprise rule validation, and live local Ollama model inference.

---

## 2. Running Automated Tests

Run the full pytest suite from the project root:
```powershell
.\venv\Scripts\python -m pytest tests/ -v
```

To run a specific test module:
```powershell
.\venv\Scripts\python -m pytest tests/unit/test_ollama_llm.py -v -s
```

To run with full execution time benchmarks:
```powershell
.\venv\Scripts\python -m pytest tests/ --durations=5
```

---

## 3. Test Suite Inventory

| Test Module | Coverage Scope | Key Assertions |
| :--- | :--- | :--- |
| `tests/unit/test_main.py` | FastAPI application startup & health | `/health` returns status `ok`, `/api/v1/health` returns version `v1` |
| `tests/unit/test_docs.py` | Project creation & upload validation | Project creation, retrieval, and non-PDF rejection (`400 Bad Request`) |
| `tests/unit/test_ollama_llm.py` | Local Ollama provider & model diagnostics | Model `llama3.2:3b` reachability, diagnostic test generation, latency, grounded prompting |
| `tests/unit/test_document_pipeline.py` | Full document ingestion & vector search | Synthetic 2-page PDF generation, PyMuPDF text extraction, chunking with page metadata, ChromaDB indexing, entity extraction, enterprise findings, and deletion cleanup |
| `tests/unit/test_comparison_and_reports.py` | Specification diffs, history, and exports | Rejection of same-document comparison, calculation of added/removed/modified entities, comparison history retrieval, CSV formula injection escaping, report download |
| `tests/unit/test_settings_and_diagnostics.py` | Settings validation, diagnostics, reviews | Rejection of `overlap >= chunk_size` (`400 Bad Request`), persistence to `data/settings.json`, `/api/v1/diagnostics` verification, finding & entity review persistence |

---

## 4. Synthetic PDF Generation in Tests
Tests use synthetic, isolated PDFs generated programmatically in-memory or in temporary directories using PyMuPDF:
```python
doc = pymupdf.open()
page = doc.new_page()
page.insert_text((50, 72), "Software Component PowertrainManager_SWC handles engine operations.")
doc.save(filepath)
```
- **No confidential corporate specifications** are committed to the repository.
- Synthetic documents contain explicit architectural keywords to test entity regexes and rule checks deterministically.

---

## 5. Mocking Strategy
- **Unit Isolation**: Unit tests for API schemas and validation use in-memory SQLite fixtures.
- **Real Local Integration**: Tests for Ollama verify the actual running instance at `http://localhost:11434` without mocking, guaranteeing true local hardware readiness.
- **CSV Security**: Tests explicitly verify that formula injection characters (`=, +, -, @`) are neutralized with a leading single quote (`'`).
