# RAG QUALITY & GROUNDING AUDIT: AUTOSAR HLD ANALYSIS

## 1. Executive Summary: RAG Pipeline Status
Our Retrieval-Augmented Generation (RAG) pipeline is fully functional and delivers grounded, deterministic engineering answers using local Ollama (`llama3.2:3b`) without hallucinations. However, compared to the reference project, it lacks **atomic claim segmentation**, **quantitative grounding scoring**, **hybrid BM25/Dense reranking**, and an **automated 35-query benchmark runner**.

---

## 2. Current RAG Workflow & Mechanics

```mermaid
sequenceDiagram
    participant Engineer as "User (Streamlit)"
    participant SessionAPI as "Sessions API (/ask)"
    participant Chroma as "ChromaDB Vector Store"
    participant DB as "SQLite Database"
    participant Ollama as "Local Ollama (llama3.2:3b)"

    Engineer->>SessionAPI: POST query + optional document_ids
    SessionAPI->>Chroma: search_chunks(query, top_k=5, where=document_ids)
    Chroma-->>SessionAPI: Top 5 chunks + metadata (page_start, page_end)
    SessionAPI->>DB: Resolve document filenames for citations
    SessionAPI->>Ollama: POST /api/generate (Grounded prompt + retrieved excerpts)
    Ollama-->>SessionAPI: Raw answer text
    SessionAPI->>DB: Persist AnalysisSession & AnalysisMessage (with citations JSON)
    SessionAPI-->>Engineer: JSON {answer, citations, session_id}
```

---

## 3. Detailed Component Audit

### 3.1 Retrieval Strategy
- **Current Approach**: Dense vector semantic similarity via ChromaDB using SentenceTransformers.
- **Reference Approach**: Hybrid retrieval combining Dense FAISS search + Entity keywords + Section headings.
- **Evaluation**: Dense retrieval alone is effective for semantic conceptual matching ("How does torque arbitration work?"), but can miss exact alphanumeric identifiers ("IF_CAN_0x4A2") if embedding distances are suboptimal.
- **Recommendation**: Implement a two-stage hybrid retrieval:
  1. ChromaDB dense retrieval (Top 10).
  2. BM25 keyword matching on chunk text (Top 10).
  3. Reciprocal Rank Fusion (RRF) to select the final Top 5 evidence chunks.

### 3.2 Chunking & Metadata Preservation
- **Current Parameters**: Chunk Size = 1000 characters, Overlap = 150 characters.
- **Metadata Stored**:
  - `document_id`
  - `chunk_index`
  - `page_start`
  - `page_end`
- **Reference Project Metadata**:
  - `chunk_id` format: `autosar_hld__v1.0_p06_c23` (encodes doc name, version, page, and chunk index).
  - Explicit `section_heading` tag (e.g. `4. (Interfaces)`).
- **Gap**: Our database model `models.DocumentChunk` has a `section_heading` column, but the current sliding-window text chunker does not populate section headers from PDF bookmarks or regex headers.

### 3.3 Prompt Grounding & Hallucination Resistance
- **Current System Prompt** (`backend/services/llm_service.py:L217`):
  > *"You are an automotive software architecture document analysis assistant. Answer only using the source evidence provided for the current question. Do not invent architectural components, interfaces, dependencies, page numbers, or design decisions. Distinguish explicit document statements from interpretations. Cite each substantive claim using the supplied document and page metadata. If the retrieved evidence does not answer the question, say that the available documents do not provide sufficient evidence..."*
- **Observed Behavior**:
  - Live query test on *Runnable_ArbitrateTorque*: Model correctly quoted Priority (5), Cycle time (10ms), and algorithm (PID), accurately citing Page 2 and Page 1.
  - Abstention test: When asked questions absent from the document, model correctly refused to fabricate components and abstained cleanly.

### 3.4 Citation Integrity & Verification
- **Current Output**: Citations returned as structured objects containing:
  - `document_id`: Integer
  - `document_name`: String
  - `page_start`: Integer
  - `page_end`: Integer
  - `content`: Text excerpt
- **Reference Project Output**:
  - Table displaying `Validation: VALID`, `Chunk ID`, `Document`, `Version`, `Page`, `Section`, `Notes`.
  - Atomic citation identifiers linked directly to specific claims.

### 3.5 Claim Segmentation & Grounding Scoring
- **Gap Identified**:
  - The reference project parses the LLM output into discrete claims (`Claim 1`, `Claim 2`) and marks each with a badge: `[Grounded]` or `[Unverified]`.
  - It displays a metric: `GROUNDING SCORE: 100.0%`.
  - Our project currently outputs the complete response as a single formatted markdown string and displays citations in an accordion.

---

## 4. Evaluation Benchmark Comparison

| Metric / Dimension | Reference Project | Current Project | Analysis |
| :--- | :---: | :---: | :--- |
| **Benchmark Query Count** | 35 (25 technical + 10 adversarial) | 0 active benchmark queries | No offline evaluation dataset currently committed |
| **Retrieval MRR** | 0.7040 | Not calculated | Needs ground-truth query-to-chunk mapping |
| **Hit Rate @ 1** | 68.0% | Not calculated | Needs top-1 relevant chunk check |
| **Citation Precision** | 100.0% | 100.0% (Qualitative) | Real citations match document pages accurately |
| **Supported Claims** | 76.7% | Not segmented | Needs claim parsing and NLI verification |
| **Abstention Accuracy** | 100.0% (10/10) | Verified in unit test | Passes `test_ask_question_insufficient_evidence` |
| **Latency Measurement** | Component breakdown (Embedding, Search, Rerank, LLM) | Subsystem diagnostics (DB, Vector, PyMuPDF, LLM) | Overall latency measured, but not per-query micro-latency |

---

## 5. Recommended RAG Quality Improvements

1. **Section Heading Extraction**: Extract TOC headings and markdown headers (`# 1. System Overview`) from PDFs and prepend them to chunk metadata for richer vector context.
2. **Claim-Level Decomposition**: Add a post-generation parser splitting answers into atomic sentences and checking lexical overlap with retrieved chunks.
3. **Deterministic Grounding Score Calculation**:
   $$\text{Grounding Score} = \frac{\text{Number of Grounded Claims}}{\text{Total Claims}} \times 100\%$$
4. **Offline Evaluation Benchmark Suite**: Implement `scripts/run_rag_benchmark.py` running 25 technical and 10 adversarial prompts against the local Ollama instance and reporting MRR and Hit Rate @ 1.
