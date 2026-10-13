# AUDIT TEST RESULTS & RUNTIME VERIFICATION LOG

## 1. Test Environment Specification
- **Operating System**: Microsoft Windows 11
- **Python Runtime**: Python 3.11.9 (64-bit)
- **Virtual Environment**: `H:\tech_pulse_project\autosar-ai\venv`
- **FastAPI Backend**: `http://127.0.0.1:8000` (Uvicorn ASGI)
- **Streamlit Frontend**: `http://localhost:8501`
- **Local LLM Engine**: Ollama daemon (`http://localhost:11434`), model `llama3.2:3b` (2.01 GB, Q4_K_M)
- **Vector Database**: ChromaDB (persistent mode, `./data/vector_store`)
- **Relational Database**: SQLite 3 (`./data/autosar_ai.db`)
- **PDF Parser**: PyMuPDF (fitz) v1.23+

---

## 2. Automated Test Suite Results (PyTest)
The complete unit test suite was executed via `pytest -v` with `PYTHONPATH='.'`.

**Execution Timestamp**: 2026-10-12 14:57:01 UTC  
**Result Summary**: **16 PASSED**, 0 FAILED, 3 deprecation warnings (Pydantic V2 config). Duration: 25.22s.

| Test ID | Module | Test Function | Purpose / Scope | Result | Observed Output |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **T01** | `test_comparison_and_reports.py` | `test_csv_formula_injection_sanitization` | Verifies leading `=`, `+`, `-`, `@` characters are neutralized in CSV exports | **PASS** | Dangerous strings safely prepended with single quotes (`'`) |
| **T02** | `test_comparison_and_reports.py` | `test_document_comparison_and_history` | Tests multi-document comparison API, diff calculation, and history retrieval | **PASS** | Successfully computed added/modified/removed counts |
| **T03** | `test_comparison_and_reports.py` | `test_report_generation_and_download` | Validates creation and physical file existence of CSV/JSON/PDF exports | **PASS** | File written to `./data/exports` and streamed via `FileResponse` |
| **T04** | `test_docs.py` | `test_create_project` | Validates project workspace creation | **PASS** | HTTP 200, Project ID returned |
| **T05** | `test_docs.py` | `test_get_projects` | Validates listing of project workspaces | **PASS** | HTTP 200, Project list populated |
| **T06** | `test_docs.py` | `test_upload_invalid_file` | Verifies rejection of non-PDF files | **PASS** | HTTP 400 with detail "Only PDF files are supported." |
| **T07** | `test_document_pipeline.py` | `test_chunking_and_entity_extraction` | Validates sliding window text chunker and regex entity extractor | **PASS** | Correct chunks with overlap; SWCs, Runnables, IFs identified |
| **T08** | `test_document_pipeline.py` | `test_full_document_ingestion_and_cleanup` | End-to-end PDF processing, ChromaDB indexing, and document deletion | **PASS** | Document parsed, status updated to `READY`, chunks cleaned on delete |
| **T09** | `test_main.py` | `test_health_check` | Root API ping | **PASS** | `{"status": "ok"}` |
| **T10** | `test_main.py` | `test_health_check_v1` | API v1 ping | **PASS** | `{"status": "ok", "api_version": "v1"}` |
| **T11** | `test_ollama_llm.py` | `test_active_provider_info` | Verifies local Ollama configuration resolution | **PASS** | Returns provider `ollama`, model `llama3.2:3b`, `is_local=True` |
| **T12** | `test_ollama_llm.py` | `test_ollama_connection_diagnostic` | Live HTTP ping to local Ollama daemon tags endpoint | **PASS** | Status `PASS`, `model_exists=True`, measured latency ~15ms |
| **T13** | `test_ollama_llm.py` | `test_ask_question_insufficient_evidence` | Verifies refusal/abstention when context lacks answers | **PASS** | System does not hallucinate; returns abstention notice |
| **T14** | `test_settings_and_diagnostics.py` | `test_settings_validation_and_persistence` | Validates chunk size > overlap constraint and settings storage | **PASS** | Rejects invalid overlap with HTTP 400; valid settings saved |
| **T15** | `test_settings_and_diagnostics.py` | `test_system_diagnostics_endpoint` | End-to-end diagnostic of DB, Vector store, PyMuPDF, and LLM | **PASS** | Overall status `PASS`; all 4 subsystems operational |
| **T16** | `test_settings_and_diagnostics.py` | `test_findings_and_entity_review` | Verifies human review workflow on findings and extracted entities | **PASS** | Review statuses updated to `confirmed`/`resolved` |

---

## 3. End-to-End Live Runtime Verification

### Test E2E-01: Document Ingestion & Deduplication
- **Input**: `data/AUTOSAR_Adaptive_Powertrain_HLD.pdf` (3 pages, ASIL D, 10 architectural components).
- **Execution**: Uploaded via API `POST /api/v1/projects/1/documents`.
- **Result**:
  - Document ID: 5
  - Status: `READY`
  - SHA-256 Hash: `b4685c0519b70588792cb3d4a15696cbd92adc504b52683b207afefcea4f62aa`
  - Chunks Generated: 11 chunks inserted into ChromaDB `project_1`.
  - Re-upload Test: Re-uploading the same file returned the existing document without creating duplicate records.

### Test E2E-02: Grounded Engineering Query with Local Ollama
- **Query**: *"What is the priority, cycle time, and function of Runnable_ArbitrateTorque and which software components coordinate torque?"*
- **Execution**: Submitted via `POST /api/v1/projects/1/ask`.
- **Observed Response**:
  > *"According to the document, the following information is provided about Runnable_ArbitrateTorque:*
  > *- Priority: 5*
  > *- Cycle time: 10ms*
  > *- Function: Executes the core PID arbitration algorithm, evaluates torque.*
  > *Additionally, the document states that Runnable_ArbitrateTorque is scheduled as a periodic runnable.*
  > *According to the document, the following software components coordinate torque:*
  > *- PowertrainManager_SWC*
  > *- TorqueArbitration_SWC..."*
- **Citations Returned**:
  - Citation 1: `AUTOSAR_Adaptive_Powertrain_HLD.pdf`, Page 2 (*Section 3: Runnables and Task Scheduling*)
  - Citation 2: `AUTOSAR_Adaptive_Powertrain_HLD.pdf`, Page 1 (*Section 2: Software Components*)
- **Status**: **PASS (100% Grounded, zero hallucination)**.

### Test E2E-03: Architectural Rule Validation
- **Execution**: Triggered during document processing in `document_service.py`.
- **Observed Findings**:
  - `Insecure IPC`: Found mention of shared memory / direct memory access bypassing RTE.
  - `Missing Boundary Definition`: Found unbounded buffer reference without explicit upper bound.
  - `Circular Dependency`: Evaluated coupling between `PowertrainManager_SWC` and `TorqueArbitration_SWC`.
- **Status**: **PASS**.

---

## 4. Tests That Could Not Be Performed & Justification
1. **Google Gemini Live Cloud Generation**:
   - *Reason*: `LLM_API_KEY` is not configured in `.env`.
   - *Impact*: Minor; local Ollama (`llama3.2:3b`) fully handles generation without external dependencies.
2. **Scanned PDF OCR with Tesseract**:
   - *Reason*: Tesseract binary is not installed in the system PATH; test PDFs were digital text-based PDFs.
   - *Impact*: Low for standard digital HLD documents.
3. **35-Query Evaluation Benchmark Suite**:
   - *Reason*: The benchmark evaluation dataset and calculation runner are not yet implemented in the current codebase (classified as Phase 4).
