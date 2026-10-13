# AUTOSAR AI — End-User Operational Guide

Welcome to the **AUTOSAR AI — HLD Document Intelligence Platform**. This guide explains how automotive software engineers and architects can use every page of the application to analyze High-Level Design (HLD) specifications, extract architecture models, audit compliance rules, and interact with the local AI Assistant.

---

## 1. Dashboard (`frontend/pages/1_Dashboard.py`)

### Purpose
The Dashboard provides an immediate overview of project health, document processing volume, total extracted components, open architectural findings, and real-time subsystem diagnostics.

### Important Controls & What They Do
- **Total Documents Metric**: Shows the total count of PDF specifications registered in the active project.
- **Processed Documents Metric**: Counts documents whose status is `READY` (chunked, indexed in vector store, and scanned for entities).
- **Architecture Entities Metric**: Total Software Components, Runnables, and Interfaces extracted.
- **Open Findings Metric**: Active rule violation flags awaiting engineering review.
- **Recent Documents Table**: Lists the 5 most recent documents with status badges (`READY`, `PROCESSING`, `FAILED`).
- **"Run Full Diagnostics" Button**: Triggers live health checks across FastAPI, SQLite, ChromaDB, Ollama (`llama3.2:3b`), and PyMuPDF.

### Step-by-Step Usage
1. Open `http://localhost:8501` in your browser.
2. Review the top KPI cards for your project.
3. Click **"Run Full Diagnostics"** in the right column to verify that Ollama and the local database are operational.
4. Click any quick action to navigate to Document Ingestion or the AI Assistant.

---

## 2. Document Repository (`frontend/pages/2_Documents.py`)

### Purpose
Upload, validate, inspect, reprocess, and delete automotive specifications in PDF format.

### Important Controls & What They Do
- **Project Dropdown**: Displays the active workspace context (e.g. `AUTOSAR Adaptive Platform HLD`).
- **Status Filter**: Filters documents by `All`, `READY`, `PROCESSING`, `FAILED`, or `UPLOADED`.
- **Search Input**: Instantly filters specifications by file name.
- **Drag-and-Drop PDF Uploader**: Uploads a PDF to the platform (enforces a 50MB safety limit).
- **"Upload & Process" Button**: Saves the file, computes SHA256 checksums, and launches background ingestion.
- **"🔄 Reprocess" Button**: Re-runs the PyMuPDF extraction, chunking, and rule validation pipeline.
- **"🗑️ Delete" Button**: Deletes the PDF file, all extracted chunks from SQLite, all embeddings from ChromaDB, and associated findings.

### Step-by-Step Usage
1. Drag and drop your AUTOSAR HLD or SRS PDF into the uploader box.
2. Click **"Upload & Process"**.
3. The document status transitions to `PROCESSING`, PyMuPDF extracts text page-by-page, generates chunks, populates the vector database, extracts components, and updates the status to `READY`.
4. Click on the document expander to view page count, SHA256 hash, and options to Reprocess or Delete.

---

## 3. Architecture Explorer (`frontend/pages/3_Architecture_Explorer.py`)

### Purpose
Examine all extracted AUTOSAR entities—Software Components (`SWC`), Runnables, and Interfaces—along with their source provenance and review status.

### Important Controls & What They Do
- **Entity Type Selector**: Filter by `All`, `Software Component`, `Runnable`, or `Interface`.
- **Search Components**: Search by component name (e.g., `PowertrainManager_SWC`).
- **Entity Card & Excerpt**: Expand any entity to view its confidence score, source page number, and original document excerpt.
- **Review Verification Buttons**:
  - `✅ Confirm`: Validates the entity as a verified architectural asset.
  - `❌ Reject`: Flags the extraction as a false positive or unverified entity.
  - `⏳ Reset Pending`: Reverts review status to unverified.

---

## 4. AI Assistant (`frontend/pages/4_AI_Assistant.py`)

### Purpose
Conduct grounded question-answering with conversational AI powered by your local Ollama `llama3.2:3b` model.

### Important Controls & What They Do
- **Local Engine Banner**: Confirms offline inference using Ollama `llama3.2:3b`.
- **Scope Analysis Selector**: Restricts semantic search to a specific document or queries across all project documents.
- **Chat Input Bar**: Submit any engineering or architecture question.
- **Interactive Suggested Questions**: Click any suggestion (e.g. *"Summarize the AUTOSAR architecture."*) to immediately run the query.
- **Source Citations Expander**: Every substantive claim displays the exact document name, page start/end numbers, and source text excerpt used to ground the answer.
- **"Clear Chat History" Button**: Resets the chat display.

---

## 5. Document Comparison (`frontend/pages/5_Comparisons.py`)

### Purpose
Compute deterministic architectural differences across two revisions of an AUTOSAR design specification.

### Important Controls & What They Do
- **"Document Comparison" Tab**:
  - **Baseline Document**: Select the original specification (e.g., v1).
  - **Comparison Document**: Select the revised specification (e.g., v2).
  - **"Compare Documents" Button**: Analyzes component differences.
  - **Results Metrics**: Displays exact counts of Added, Removed, and Modified entities.
  - **Component Diffs**: Detailed lists of added components, removed components, and modified excerpts.
- **"Comparison History" Tab**:
  - Displays all past comparison runs with dates and result summaries.
  - **"Load This Result" Button**: Restores previous comparison diffs without re-computation.

---

## 6. Findings & Validation (`frontend/pages/6_Findings.py`)

### Purpose
Review enterprise rule violations detected during automated document parsing (e.g., Insecure IPC, missing array bounds, circular dependencies).

### Important Controls & What They Do
- **Severity Filter**: Filter by `High`, `Medium`, or `Low`.
- **Status Filter**: Filter by `open`, `confirmed`, `resolved`, or `rejected`.
- **Finding Detail Expander**: View finding type, description, and JSON evidence trace.
- **Reviewer Status Dropdown & Notes Input**: Update decision and record engineering justification.
- **"💾 Save Review Decision" Button**: Persists decisions directly to SQLite.

---

## 7. Reports & Exports (`frontend/pages/7_Reports.py`)

### Purpose
Generate and download audit reports in CSV, JSON, or text format.

### Important Controls & What They Do
- **Report Type**: Choose `Architecture Summary`, `Findings Report`, or `Dependency Matrix`.
- **Format**: Choose `CSV`, `JSON`, or `PDF` (formatted text).
- **"Generate Report" Button**: Compiles live project data into an export artifact with spreadsheet formula injection protection.
- **"⬇️ Download" Button**: Downloads the generated report directly to your computer.

---

## 8. Settings & Diagnostics (`frontend/pages/8_Settings.py`)

### Purpose
Configure document extraction chunking parameters, enterprise validation rules, and run self-test diagnostics.

### Important Controls & What They Do
- **Chunk Size Slider**: Target character length per text chunk (200–2500).
- **Chunk Overlap Slider**: Overlapping characters between consecutive chunks (0–500, strictly `< chunk_size`).
- **Table Extraction & OCR Checkboxes**: Toggle table parsing and image extraction.
- **"Save Extraction Parameters"**: Persists configuration to `data/settings.json` and updates runtime settings immediately.
- **Enterprise Rule Checkboxes**: Enable or disable circular dependency checks, secure IPC matching, and array bounds rules.
- **"Run Diagnostic Self-Test"**: Queries `/api/v1/diagnostics` and prints a real-time health JSON report.
