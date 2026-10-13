# MISSING FEATURES & TECHNICAL RECOMMENDATIONS

This document provides actionable engineering specifications for every missing or partially implemented feature identified during the parity audit against the reference project.

---

## 1. Feature Specifications

### Feature 1: Granular Ports & Signals Modeling
- **Problem Solved**: AUTOSAR architecture relies heavily on port-signal interfaces (`PPort`, `RPort`, `SenderReceiver`, `ClientServer`). Currently, our extractor extracts high-level SWCs and Interfaces, but not individual port names, directions (Input/Output), or signals with data types.
- **Engineering Value**: Allows engineers to verify whether port contracts are satisfied, detect missing signal producers/consumers, and identify signal data type mismatches across versions (`float32 -> float64`).
- **Technical Approach**:
  1. Add regex and token extractors in `backend/services/document_service.py` targeting Port keywords (`Port:`, `RPort_`, `PPort_`, `Input`, `Output`, `Direction:`) and Signal definitions (`Signal:`, `Type:`, `float32`, `uint16`).
  2. Enhance `models.ArchitectureEntity` to support entity types: `"Port"` and `"Signal"`, or add dedicated tables `architecture_ports` and `architecture_signals`.
  3. Render dedicated sub-tab `Ports & Signals` in `Architecture_Explorer.py` with columns: `Port Name`, `Component`, `Direction`, `Interface`, `Carried Signals`, `Version`, `Page`, `Chunk ID`.
- **Complexity**: High
- **Files Affected**:
  - `backend/models/domain.py`
  - `backend/services/document_service.py`
  - `frontend/pages/3_Architecture_Explorer.py`
- **Acceptance Criteria**: Ingesting an HLD specification extracts Port names, directions, associated interfaces, and carried signals into a filterable table.

---

### Feature 2: Architecture Topology Diagram (Mermaid Graph)
- **Problem Solved**: Engineers must mentally reconstruct dependencies between software components and interfaces from tabular lists.
- **Engineering Value**: Visual graph representation clearly displays architecture layers, coupling, circular links, and newly added or renamed components at a glance.
- **Technical Approach**:
  1. Populate `models.ArchitectureRelationship` during document processing when SWCs reference interfaces or other components (`DEPENDS_ON`, `REQUIRES`, `PROVIDES`).
  2. Implement a helper in `frontend/utils/ui.py` or `3_Architecture_Explorer.py` that formats active entities and relationships into Mermaid syntax:
     ```mermaid
     graph TD
         subgraph "Software Components - v2.0"
             VC[VehicleControl]
             SM[SensorManager]
         end
         subgraph "AUTOSAR Interfaces"
             VDI[VehicleDataInterface]
         end
         VC -->|DEPENDS_ON| SM
         SM -->|PROVIDES| VDI
         VC -->|REQUIRES| VDI
     ```
  3. Render the graph inside `3_Architecture_Explorer.py` alongside the `Directed Graph Edges` table.
- **Complexity**: Medium
- **Files Affected**:
  - `backend/services/document_service.py`
  - `backend/api/v1/entities.py`
  - `frontend/pages/3_Architecture_Explorer.py`
- **Acceptance Criteria**: The Architecture Explorer displays a rendered Mermaid topology diagram matching extracted entities and relationships with interactive filtering.

---

### Feature 3: Query-Level Engineer Review & Audit History
- **Problem Solved**: Currently, human review status exists only for Entities (`confirmed`/`rejected`) and Findings (`resolved`/`open`), but not for individual AI Assistant queries and generated answers.
- **Engineering Value**: Essential for safety-critical ISO 26262 compliance where human-in-the-loop sign-off (Accepted, Rejected, Needs Modification) must be persisted with reviewer ID, feedback, and timestamp.
- **Technical Approach**:
  1. Add columns to `models.AnalysisMessage`: `review_decision` (`accepted`, `rejected`, `needs_modification`), `reviewer_id`, `review_feedback`, `corrected_facts`.
  2. Add an inline sign-off form below AI assistant responses in `frontend/pages/4_AI_Assistant.py`.
  3. Add an audit log endpoint `/api/v1/audit/reviews` returning all reviewed Q&A records.
  4. Create a dedicated `Review Audit History` page or tab displaying Record ID, Question, Decision, Engineer ID, Feedback, Corrections, and Timestamp.
- **Complexity**: Medium
- **Files Affected**:
  - `backend/models/domain.py`
  - `backend/api/v1/sessions.py`
  - `frontend/pages/4_AI_Assistant.py`
  - `frontend/pages/6_Findings.py` or new `Review_Audit.py`
- **Acceptance Criteria**: Engineer can click `Accepted` or `Needs Modification` on an assistant answer, enter their Engineer ID and notes, and view the persistent log in the audit history table.

---

### Feature 4: Claim-Level Segmentation & Grounding Score Metric
- **Problem Solved**: Answers currently appear as monolithic paragraphs, making it hard for engineers to quickly spot which individual statements are backed by citations versus unverified interpretations.
- **Engineering Value**: Increases trust by explicitly labeling each claim as `[Grounded]` or `[Unverified]`, accompanied by a quantitative `Grounding Score: 100.0%`.
- **Technical Approach**:
  1. Add post-processing logic in `backend/services/llm_service.py` that parses the LLM output into numbered claims.
  2. For each claim, check lexical and semantic token overlap against retrieved context chunks.
  3. Calculate `Grounding Score = (grounded_claims / total_claims) * 100`.
  4. Return `claims: [{"claim_text": "...", "status": "Grounded", "citations": ["chunk_1"]}]`.
  5. Render metric cards (`CONFIDENCE`, `GROUNDING SCORE`, `EVIDENCE RECORDS`) and claim cards in `4_AI_Assistant.py`.
- **Complexity**: Medium
- **Files Affected**:
  - `backend/services/llm_service.py`
  - `backend/api/v1/sessions.py`
  - `frontend/pages/4_AI_Assistant.py`
- **Acceptance Criteria**: Query responses render metric cards (Confidence, Grounding Score %) and discrete claim cards with clickable citation tags.

---

### Feature 5: Offline RAG Evaluation Benchmark Dashboard
- **Problem Solved**: No continuous quantitative verification of retrieval quality, leading to regression risk when chunking or embedding configurations change.
- **Engineering Value**: Objectively measures Information Retrieval quality (MRR, Hit Rate @ 1) and safety (Abstention accuracy on adversarial prompts).
- **Technical Approach**:
  1. Create `data/evaluation/benchmark_35_queries.json` containing 25 domain technical questions with ground-truth chunk IDs and 10 out-of-scope/adversarial prompts.
  2. Implement `backend/services/evaluation_service.py`:
     - Calculates Mean Reciprocal Rank (MRR): $MRR = \frac{1}{|Q|}\sum_{i=1}^{|Q|}\frac{1}{\text{rank}_i}$
     - Calculates Hit Rate @ 1: Proportion of queries where the rank-1 chunk is relevant.
     - Calculates Abstention Accuracy: Proportion of adversarial queries rejected.
     - Profiles micro-latencies (Embedding, Vector Search, LLM inference).
  3. Create API endpoint `POST /api/v1/evaluation/recompute`.
  4. Render an Evaluation Dashboard page with summary metrics and latency profiles.
- **Complexity**: High
- **Files Affected**:
  - `backend/services/evaluation_service.py`
  - `backend/api/v1/evaluation.py`
  - `frontend/pages/Evaluation_Dashboard.py`
- **Acceptance Criteria**: Clicking `Recompute Benchmark` runs the 35 queries against the local Ollama RAG pipeline and displays live MRR, Hit Rate @ 1, and latency cards.

---

### Feature 6: Inline Report Export (Markdown / JSON)
- **Problem Solved**: Currently, downloading reports requires navigating away from the chat interface to `7_Reports.py`.
- **Engineering Value**: Allows engineers to immediately export the current question, answer, claims, citations, and sign-off decision as an official audit report artifact.
- **Technical Approach**:
  1. In `4_AI_Assistant.py`, generate JSON and Markdown export strings from the current assistant message.
  2. Add `st.download_button` for `Download JSON Report` (`autosar_rag_report.json`) and `Download Markdown Report` (`autosar_rag_report.md`).
- **Complexity**: Low
- **Files Affected**:
  - `frontend/pages/4_AI_Assistant.py`
- **Acceptance Criteria**: Directly downloading Markdown produces the exact report format shown in `WhatsApp Image 2026-10-12 at 8.07.53 PM.jpeg`.
