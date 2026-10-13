# AUTOSAR AI — Internal Developer & Architectural Guide

## 1. Architectural Philosophy
AUTOSAR AI is engineered around modularity, local data privacy, and deterministic software engineering. The platform separates client rendering (Streamlit) from computational and storage workloads (FastAPI, SQLite, ChromaDB, Ollama).

---

## 2. Universal Data Flow Pattern
Every user action in the application adheres strictly to the following end-to-end pipeline:

$$\text{User Action} \rightarrow \text{Streamlit Page} \rightarrow \text{REST Client} \rightarrow \text{FastAPI Endpoint} \rightarrow \text{Business Logic / Service Layer} \rightarrow \text{Database / Vector Store / Ollama} \rightarrow \text{JSON Response} \rightarrow \text{UI State Rendering}$$

---

## 3. End-to-End Workflow Traces

### Workflow 1: Document Upload & Ingestion Pipeline
1. **User Action**: User drops a PDF into `frontend/pages/2_Documents.py` and clicks **"Upload & Process"**.
2. **Streamlit Component**: Reads bytes from `st.file_uploader`, packages multipart form data, and submits `POST http://127.0.0.1:8000/api/v1/projects/{id}/documents`.
3. **FastAPI Route**: `backend/api/v1/documents.py::upload_document`:
   - Validates file extension `.pdf` and maximum size against `settings.MAX_UPLOAD_MB` (50MB).
   - Computes SHA256 checksum and saves PDF to `data/uploads/{project_id}_{filename}`.
   - Inserts `models.Document` row with status `UPLOADED`.
   - Schedules background task: `background_tasks.add_task(process_document, doc.id)`.
4. **Service Logic**: `backend/services/document_service.py::process_document`:
   - Opens PDF using `pymupdf.open(doc.storage_path)`.
   - Iterates pages (1-indexed), extracting text and recording exact page boundaries.
   - Chunks text using `chunk_text()` based on `settings.CHUNK_SIZE` (1000) and `settings.CHUNK_OVERLAP` (150).
   - Inserts rows into `models.DocumentChunk` with `page_start`, `page_end`, and `content_hash`.
   - Calls `vector_store_service.py::add_chunks` to index embeddings in ChromaDB persistent collection `project_{id}`.
   - Runs `extract_entities_from_text()` using AUTOSAR regex heuristics to extract SWCs, Runnables, and Interfaces into `models.ArchitectureEntity`.
   - Runs `run_enterprise_rule_checks()` to scan for Insecure IPC, missing bounds, and circular dependencies, writing `models.Finding` records.
   - Sets `Document.status = "READY"` and `Document.page_count`.
5. **UI Rendering**: Status polling or page rerun displays status badge `badge-success` and enables inspection.

---

### Workflow 2: Grounded AI Assistant Query (Local Ollama RAG)
1. **User Action**: User submits a query or clicks a suggested question in `frontend/pages/4_AI_Assistant.py`.
2. **Streamlit Component**: Appends message to `st.session_state.messages` and calls `POST /api/v1/projects/{id}/ask` with payload `{"query": prompt, "document_ids": [...]}`.
3. **FastAPI Route**: `backend/api/v1/sessions.py::ask_assistant`:
   - Calls `vector_store_service.py::search_chunks(project_id, query, top_k=5, document_ids)`.
   - ChromaDB returns top-k matching passages and metadata (`document_id`, `page_start`, `page_end`).
   - Resolves document titles from SQLite and constructs grounded context with strict attribution headers.
   - Invokes `backend/services/llm_service.py::ask_question(query, context)`.
4. **LLM Provider**: `llm_service.py`:
   - Prepares system instructions forbidding hallucination or unverified claims.
   - Dispatches HTTP POST to local Ollama API: `http://localhost:11434/api/generate` with model `llama3.2:3b`.
   - Captures local response within 120-second timeout.
5. **Persistence**:
   - Records session in `models.AnalysisSession`.
   - Records user query and assistant answer with JSON citations in `models.AnalysisMessage`.
6. **UI Rendering**: Assistant answer renders with stream effect, accompanied by an expandable **"📚 Source Citations"** widget linking directly to source documents and page numbers.

---

### Workflow 3: Specification Comparison & History
1. **User Action**: User chooses baseline and comparison PDFs in `frontend/pages/5_Comparisons.py` and clicks **"Compare Documents"**.
2. **FastAPI Route**: `backend/api/v1/comparisons.py::create_comparison`:
   - Validates that baseline and comparison documents are distinct.
   - Fetches all `models.ArchitectureEntity` records for both documents.
   - Maps entities by `(type, name)` and computes set differences:
     - `added`: Entities in comparison document but not baseline.
     - `removed`: Entities in baseline document but not comparison.
     - `modified`: Entities present in both with changed excerpts or descriptions.
   - Serializes structured diff into `models.DocumentComparison.results_json`.
3. **UI Rendering**: Displays KPI metrics (Added, Removed, Modified) and detailed component diff tables. Past runs are saved in SQLite and visible under the **"Comparison History"** tab.

---

### Workflow 4: Findings Review Workflow
1. **User Action**: User reviews a rule finding in `frontend/pages/6_Findings.py`, selects a new status (`confirmed`, `resolved`, `rejected`), enters notes, and clicks **"Save Review Decision"**.
2. **FastAPI Route**: `backend/api/v1/findings.py::update_finding`:
   - Executes `PATCH /api/v1/findings/{finding_id}`.
   - Updates `Finding.review_status` and `Finding.reviewer_comments` in SQLite.
3. **UI Rendering**: Success message displayed and badge updates to `badge-success` or `badge-error`.

---

### Workflow 5: Report Export & Formula Sanitization
1. **User Action**: User selects Report Type and Format (`CSV`, `JSON`, `PDF`) in `frontend/pages/7_Reports.py` and clicks **"Generate Report"**.
2. **FastAPI Route**: `backend/api/v1/reports.py::create_report`:
   - Queries relevant entities or findings from SQLite.
   - For CSV exports, runs `sanitize_csv_cell()` to prefix cells starting with `=, +, -, @, \t, \r` with `'` to prevent spreadsheet formula injection.
   - Writes generated file to `data/exports/` and records `models.Report`.
3. **Download**: `st.download_button` calls `GET /api/v1/reports/{id}/download` returning the actual file.

---

## 4. Subsystem Reference

### Core Database Models (`backend/models/domain.py`)
- `Project`: Workspaces isolating documents and architecture entities.
- `Document`: Uploaded PDF metadata, storage path, SHA256 checksum, page count, and status.
- `DocumentChunk`: Text slices with page start/end and content hashes.
- `ArchitectureEntity`: Extracted SWCs, Runnables, and Interfaces with source page and excerpt.
- `ArchitectureRelationship`: Connections between components.
- `Finding`: Architectural defect flags from enterprise rule validation.
- `DocumentComparison`: Diff runs between two document versions.
- `Report`: Exported audit artifacts.

### Vector Storage (`backend/services/vector_store_service.py`)
- Local disk persistence at `settings.VECTOR_STORE_DIR` (`./data/vector_store`).
- Collections partitioned by project: `project_{id}`.
- Chunks indexed with metadata: `{"document_id": doc_id, "page_start": p, "page_end": p}`.
- Deletions scoped by document ID using `collection.delete(where={"document_id": id})`.
