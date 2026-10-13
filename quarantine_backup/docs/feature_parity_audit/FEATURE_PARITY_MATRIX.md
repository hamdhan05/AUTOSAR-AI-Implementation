# FEATURE PARITY MATRIX: AUTOSAR HLD INTELLIGENCE PLATFORM

This matrix details the item-by-item comparison between the reference project (demonstrated in `auto_sar/` screenshots) and our current implementation.

### Status Definitions
- **VERIFIED COMPLETE**: Implementation and runtime behavior fully confirmed.
- **PARTIALLY IMPLEMENTED**: Functional, but missing specific sub-features.
- **PRESENT, DIFFERENT APPROACH**: Capability exists through an alternative architectural pattern.
- **MISSING**: No equivalent implementation exists in the current repository.
- **UI ONLY / MOCKED**: Front-facing element without real underlying backend logic.

---

## 1. Global Navigation & Configuration Sidebar

| # | Feature | Reference Project Capability | Current Project Status | Evidence & Source Location | Gaps & Next Action | Complexity | Priority |
|---|---|---|---|---|---|:---:|:---:|
| 1.1 | **Top-Level Navigation** | 7 main tabs (`Overview`, `HLD Ingestion`, `Architecture Query`, `Architecture Explorer`, `Engineering Evaluation`, `Audit & System`, `Engineering Reports`) | **PRESENT, DIFFERENT APPROACH** | Streamlit multi-page sidebar in `frontend/pages/` (8 pages: Dashboard, Documents, Architecture Explorer, AI Assistant, Comparisons, Findings, Reports, Settings) | Functionality matches; layout uses sidebar routing rather than horizontal top tabs. | Low | P3 |
| 1.2 | **LLM Provider Selector** | Global sidebar dropdown (`gemini` / `ollama`) dynamically switching execution model | **PRESENT, DIFFERENT APPROACH** | Configured via `.env` (`LLM_PROVIDER`, `LLM_MODEL`) and backend `settings.py`; tested via `/diagnostics` | Switching requires editing `.env` or settings API rather than an on-the-fly session dropdown. Add session dropdown if needed. | Medium | P2 |
| 1.3 | **LangChain Orchestration Toggle** | Checkbox in sidebar (`USE LANGCHAIN ORCHESTRATION`) | **MISSING** | No LangChain orchestration layer; queries call direct REST endpoints (`/api/v1/projects/{id}/ask` and `llm_service.py`) | Current direct prompt execution is faster and lower-overhead. Implement LangChain LCEL chain only if multi-step tools are needed. | Medium | P3 |
| 1.4 | **HLD Version Filtering** | Global dropdown (`All Versions`, `1.0`, `2.0`) restricting retrieval scope | **PARTIALLY IMPLEMENTED** | `document_ids` filter parameter supported in `/ask` API and `search_chunks`; document selection available in `AI_Assistant.py` | Need explicit document specification version tagging (`version_label`) in ChromaDB metadata. | Low | P1 |
| 1.5 | **Top-K Evidence Slider** | Slider (1-10) dynamically controlling number of retrieved evidence chunks | **PARTIALLY IMPLEMENTED** | Configured via `.env` (`TOP_K=5`) and `backend/api/v1/sessions.py:L30` | Static configuration in `.env` rather than runtime UI slider. Can expose slider directly on AI Assistant page. | Low | P2 |
| 1.6 | **Retrieval Strategy Selector** | Radio option (`HYBRID (DENSE + ENTITY + SECTION)` vs `BASELINE (DENSE FAISS)`) | **MISSING** | Uses dense embedding retrieval via ChromaDB + SentenceTransformers (`all-MiniLM-L6-v2`) | No BM25/keyword lexical hybrid reranking stage. Implement BM25 + Reciprocal Rank Fusion (RRF) for hybrid retrieval. | High | P2 |
| 1.7 | **System Telemetry Card** | Displays Vector Index Chunk Count, Embedding Model, Session Provider, Backend Default, Service Status | **PARTIALLY IMPLEMENTED** | Header & Dashboard show active LLM provider and subsystem statuses via `/diagnostics` (`diagnostics.py`) | Chunk count and embedding model name not displayed in persistent sidebar card. | Low | P2 |
| 1.8 | **Header Status Badges** | Badges: `API: CONNECTED (3006 CHUNKS)`, `SESSION: GEMINI`, `API DEFAULT: OLLAMA` | **PARTIALLY IMPLEMENTED** | Dashboard shows `API Backend: Online` and provider details | Move badges into global Streamlit header or sidebar for all pages. | Low | P3 |

---

## 2. Overview / Dashboard

| # | Feature | Reference Project Capability | Current Project Status | Evidence & Source Location | Gaps & Next Action | Complexity | Priority |
|---|---|---|---|---|---|:---:|:---:|
| 2.1 | **Indexed Document Summary** | Total documents count and ingestion status breakdown | **VERIFIED COMPLETE** | `frontend/pages/1_Dashboard.py:L18-L33`, `backend/api/v1/documents.py` | Accurate metric cards and live document counts. | Low | P3 |
| 2.2 | **Architecture Entity Summary** | Extracted SWCs and component counts | **VERIFIED COMPLETE** | `1_Dashboard.py:L26`, `backend/api/v1/entities.py` | Pulls live entity count from SQLite database. | Low | P3 |
| 2.3 | **Recent Document Activity** | Table of recently uploaded specifications with status tags | **VERIFIED COMPLETE** | `1_Dashboard.py:L40-L68` | Shows top 5 recent documents with status badges (`READY`, `PROCESSING`). | Low | P3 |
| 2.4 | **Subsystem Diagnostics Widget** | Live health check verifying Database, Vector Store, PyMuPDF, and LLM | **VERIFIED COMPLETE** | `1_Dashboard.py:L72-L105`, `backend/api/v1/diagnostics.py` | Executes real runtime ping to ChromaDB, SQLite, PyMuPDF, and Ollama with latency metrics. | Low | P3 |

---

## 3. HLD Ingestion & Document Repository

| # | Feature | Reference Project Capability | Current Project Status | Evidence & Source Location | Gaps & Next Action | Complexity | Priority |
|---|---|---|---|---|---|:---:|:---:|
| 3.1 | **PDF Specification Upload** | Drag & drop PDF uploader with size limit checks | **VERIFIED COMPLETE** | `frontend/pages/2_Documents.py:L88-L105`, `backend/api/v1/documents.py:L21-L76` | Validates file type, size (`MAX_UPLOAD_MB=50`), and saves to `./data/uploads`. | Low | P3 |
| 3.2 | **Document Version Metadata Input** | Explicit `Document Specification Version` field (e.g. `1.0`, `2.0`) on upload | **PARTIALLY IMPLEMENTED** | Column `version_label` in `models.Document:L40`, but not exposed in `2_Documents.py` upload form | Add version input field to `2_Documents.py` and pass to upload endpoint. | Low | P1 |
| 3.3 | **Document Governance State Input** | Dropdown for governance state (`DRAFT`, `APPROVED`, etc.) | **MISSING** | No governance state field in `models.Document` (only processing status `READY`, `PROCESSING`, `FAILED`) | Add `governance_state` column to `Document` model (default `DRAFT`) and UI selector. | Low | P2 |
| 3.4 | **SHA-256 Deduplication** | Hash calculation preventing duplicate document indexing | **VERIFIED COMPLETE** | `backend/api/v1/documents.py:L36-L60`, `frontend/pages/2_Documents.py:L54` | Re-uploading identical file returns existing document ID and avoids duplicate chunk indexing. | Low | P3 |
| 3.5 | **PDF Structure & Text Extraction** | Page-by-page extraction with page number preservation | **VERIFIED COMPLETE** | `backend/services/document_service.py:L194-L210` using `pymupdf` | Preserves exact page numbers (`page_start`, `page_end`) for citations. | Low | P3 |
| 3.6 | **Chunking & Overlap** | Sliding window chunking with configurable size and overlap | **VERIFIED COMPLETE** | `document_service.py:L14-L29`, configurable via Settings API and `.env` | Tested and validated with chunk size 1000 and overlap 150. | Low | P3 |
| 3.7 | **Vector Indexing & Persistence** | Local embedding and vector store persistence | **VERIFIED COMPLETE** | `backend/services/vector_store_service.py:L1-L40` using `chromadb.PersistentClient` | Index persists to `./data/vector_store` and survives application restarts. | Low | P3 |
| 3.8 | **Document Repository Management** | Filter by status, search by name, Reprocess, Delete | **VERIFIED COMPLETE** | `frontend/pages/2_Documents.py:L22-L85`, `backend/api/v1/documents.py` | Complete lifecycle operations verified working. | Low | P3 |

---

## 4. Architecture Query & Grounded RAG

| # | Feature | Reference Project Capability | Current Project Status | Evidence & Source Location | Gaps & Next Action | Complexity | Priority |
|---|---|---|---|---|---|:---:|:---:|
| 4.1 | **Canonical Question Prompts** | Quick-click canonical engineering query chips | **VERIFIED COMPLETE** | `frontend/pages/4_AI_Assistant.py:L125-L135` | 5 suggested prompts directly submit grounded queries. | Low | P3 |
| 4.2 | **Evidence-Grounded Generation** | LLM generation strictly bound to retrieved context | **VERIFIED COMPLETE** | `backend/services/llm_service.py:L201-L262`, `backend/api/v1/sessions.py` | Strict prompt constraints prevent hallucinations; tested live with Ollama `llama3.2:3b`. | Low | P3 |
| 4.3 | **Automated Abstention on Insufficient Evidence** | System explicitly refrains from inventing answers when context lacks proof | **VERIFIED COMPLETE** | `backend/services/llm_service.py:L217`, verified in unit test `test_ask_question_insufficient_evidence` | Tested: returns explicit notice when relevant evidence is absent. | Low | P3 |
| 4.4 | **Traceability & Provenance Citations** | Document name, page numbers, and exact excerpts returned with answer | **VERIFIED COMPLETE** | `backend/api/v1/sessions.py:L54-L60`, `4_AI_Assistant.py:L100-L112` | Returns clickable citations with source document, start/end pages, and excerpt text. | Low | P3 |
| 4.5 | **Segmented Architectural Claims** | Answer segmented into discrete claims with individual Grounded/Unverified badges | **MISSING** | Answer returned as unified Markdown text block without atomic claim breakdown | Add claim extraction parser and lexical/NLI verification step per claim. | Medium | P1 |
| 4.6 | **Quantitative Grounding Score** | Metric card displaying Grounding Score (e.g. `100.0%`) | **MISSING** | No numerical grounding score calculation | Calculate citation coverage / lexical token overlap percentage and display metric. | Medium | P1 |
| 4.7 | **Confidence & Review Classification** | Classification badges (`HIGH`/`LOW`, `STANDARD`/`REQUIRED`) | **MISSING** | Currently only entity confidence is calculated; query response has no confidence metric | Derive query confidence from average retrieval similarity score and evidence chunk count. | Low | P1 |
| 4.8 | **Inline Report Download** | Buttons `Download JSON Report` and `Download Markdown Report` on query view | **MISSING** | Reports are generated globally on `7_Reports.py` | Add inline download buttons in `4_AI_Assistant.py` for current query and answer. | Low | P2 |
| 4.9 | **Engineer Review & Sign-Off Form** | Inline form: Decision (`Accepted`, `Rejected`, `Needs Modification`), Reviewer ID, Feedback, Corrections | **MISSING** | Review forms exist for Entities and Findings, but not for AI Assistant chat messages | Add review form below AI responses and persist to `audit_logs` and `analysis_messages`. | Medium | P1 |

---

## 5. Architecture Explorer

| # | Feature | Reference Project Capability | Current Project Status | Evidence & Source Location | Gaps & Next Action | Complexity | Priority |
|---|---|---|---|---|---|:---:|:---:|
| 5.1 | **SWCs & Interfaces Inventory** | Extracted Software Components and Interfaces with confidence scores | **VERIFIED COMPLETE** | `frontend/pages/3_Architecture_Explorer.py`, `backend/services/document_service.py:L31-L83` | Regex heuristic extraction of SWCs, Runnables, and Interfaces with confidence % and page numbers. | Low | P3 |
| 5.2 | **Interactive Entity Review** | Review actions (`Confirm`, `Reject`, `Reset Pending`) updating database state | **VERIFIED COMPLETE** | `3_Architecture_Explorer.py:L70-L84`, `backend/api/v1/entities.py:L48-L58` | Persists review status to `models.ArchitectureEntity.review_status`. | Low | P3 |
| 5.3 | **Ports & Signals Explorer** | Dedicated tab listing Port Name, Component, Direction, Interface, and Carried Signals | **MISSING** | `ArchitectureEntity` schema does not have dedicated Port/Signal columns | Extend extraction patterns to identify port declarations (`Port_`, `RPort_`, `PPort_`) and signals. | High | P1 |
| 5.4 | **Architecture Topology Graph (Mermaid)** | Visual topology diagram grouping SWCs and Interfaces with `DEPENDS_ON`, `REQUIRES`, `PROVIDES` edges | **MISSING** | No graph visualization rendered on frontend | Add Mermaid rendering block in `Architecture_Explorer.py` generating graph from extracted entities. | Medium | P1 |
| 5.5 | **Directed Graph Edges Table** | Table of graph edges with Source, Relationship, Target, Version | **PARTIALLY IMPLEMENTED** | `models.ArchitectureRelationship` exists in DB, but table is not populated or rendered in UI | Populate relationships during extraction and render table below Mermaid graph. | Medium | P2 |
| 5.6 | **Deterministic Structural Revision Diff** | Compares baseline vs revision entities; metrics for Total Changes, Added, Modified, Renamed, Removed | **PARTIALLY IMPLEMENTED** | `frontend/pages/5_Comparisons.py`, `backend/api/v1/comparisons.py` | Detects Added, Removed, and Modified entities; missing "Renamed" heuristic and signal data type diffs. | Medium | P2 |
| 5.7 | **Change Impact Analysis** | Direct and indirect dependency traversal identifying affected downstream components | **MISSING** | No dependency traversal graph algorithm implemented | Implement BFS/DFS dependency traversal over `ArchitectureRelationship` table. | High | P2 |
| 5.8 | **Architecture Rule Validation** | Enterprise rules detecting Insecure IPC, unbounded buffers, circular dependencies | **VERIFIED COMPLETE** | `backend/services/document_service.py:L85-L156`, `frontend/pages/6_Findings.py` | Automated rule checks executed on document upload; findings persisted and reviewed. | Medium | P3 |

---

## 6. Engineering Evaluation & Benchmark Dashboard

| # | Feature | Reference Project Capability | Current Project Status | Evidence & Source Location | Gaps & Next Action | Complexity | Priority |
|---|---|---|---|---|---|:---:|:---:|
| 6.1 | **35-Query Evaluation Suite** | 25 technical queries + 10 adversarial/out-of-scope prompts | **MISSING** | No automated evaluation test dataset | Create `evaluation/benchmark_dataset.json` containing 25 ground-truth and 10 adversarial queries. | Medium | P2 |
| 6.2 | **Automated Benchmark Runner** | Action `Recompute Benchmark` executing queries against current retrieval pipeline | **MISSING** | No benchmark runner endpoint | Implement `/api/v1/evaluation/run` endpoint executing benchmark offline. | Medium | P2 |
| 6.3 | **Retrieval MRR & Hit Rate @ 1** | Calculates Mean Reciprocal Rank and Hit Rate @ 1 against ground-truth chunks | **MISSING** | No MRR/Hit Rate calculation service | Add retrieval metrics evaluation module in `backend/services/evaluation_service.py`. | Medium | P2 |
| 6.4 | **Citation Precision & Supported Claims** | Measures citation validity and claim grounding percentage | **MISSING** | Citations returned without automated precision scoring | Implement automated verification comparing citation chunk text with claims. | High | P2 |
| 6.5 | **Subsystem Latency Profiling** | Measures Query Embedding, Search, Rerank, LLM Inference, and Pipeline Latency | **PARTIALLY IMPLEMENTED** | `backend/api/v1/diagnostics.py` measures real latency for Database, ChromaDB, and Ollama | Expose detailed micro-latency profiling in an evaluation dashboard tab. | Low | P2 |

---

## 7. Audit & System

| # | Feature | Reference Project Capability | Current Project Status | Evidence & Source Location | Gaps & Next Action | Complexity | Priority |
|---|---|---|---|---|---|:---:|:---:|
| 7.1 | **Review Audit History Table** | Table with Record ID, Question, Decision, Engineer ID, Feedback, Corrections, Timestamp | **MISSING** | Schema `models.AuditLog` exists, but no Q&A review logging or UI view is active | Implement endpoint `/api/v1/audit/reviews` and render history table in UI. | Low | P1 |
| 7.2 | **Audit Persistence Across Restarts** | Records stored in persistent database surviving reboots | **VERIFIED COMPLETE** | SQLite database `data/autosar_ai.db` persists all entity reviews and comparisons | Audits are durable. | Low | P3 |

---

## 8. Engineering Reports & Governance

| # | Feature | Reference Project Capability | Current Project Status | Evidence & Source Location | Gaps & Next Action | Complexity | Priority |
|---|---|---|---|---|---|:---:|:---:|
| 8.1 | **Multi-Format Export** | Export in CSV, JSON, and PDF formats | **VERIFIED COMPLETE** | `backend/api/v1/reports.py:L48-L142`, `frontend/pages/7_Reports.py` | Exports Architecture Summary, Findings, and Dependency Matrix in CSV/JSON/PDF. | Low | P3 |
| 8.2 | **CSV Injection Sanitization** | Neutralizes spreadsheet formula injection (`=`, `+`, `-`, `@`) | **VERIFIED COMPLETE** | `backend/api/v1/reports.py:L15-L22`, tested in unit tests | Fully protected. | Low | P3 |
| 8.3 | **Per-Component Engineering Report** | Report filtered to a single selected component and version | **MISSING** | Reports are project-wide rather than component-specific | Add `component_id` filter option to report generator. | Low | P2 |
| 8.4 | **Q&A Report Export (Markdown/JSON)** | Exports current Q&A session with query, answer, claims, and citations | **PARTIALLY IMPLEMENTED** | `analysis_messages` stored in DB, but no one-click download button in assistant | Add Markdown/JSON download button directly to assistant response container. | Low | P1 |
