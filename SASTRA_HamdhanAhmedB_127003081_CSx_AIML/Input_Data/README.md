# Input Data Specifications & Provenance

## 1. Overview
This directory contains sample automotive architectural specifications and the standardized query set used for testing, indexing, and evaluating the AUTOSAR AI platform.

## 2. Contents
1. **`Sample_HLD_Documents/`**:
   - `AUTOSAR_Adaptive_Powertrain_HLD.pdf`: High-Level Design document representing an Electric Vehicle (EV) Powertrain Management System structured according to AUTOSAR Adaptive Platform conventions. Includes Software Components (`PowertrainManager`, `BatteryManagement`, `TorqueArbitration`), Runnables, Client-Server & Sender-Receiver Interfaces, and Port/Signal definitions.
   - `1_Synthetic_Automotive_Architecture_RAG_Test.pdf`: Multi-page synthetic test document designed specifically for boundary testing, text extraction validation, and circular dependency checks.
2. **`Sample_Query_Set/`**:
   - `benchmark_dataset_35.json`: JSON specification of 35 evaluation queries (25 automotive domain technical queries and 10 adversarial/out-of-scope queries designed to test system abstention).
   - `sample_queries_35.csv`: Tabular spreadsheet version of the 35 benchmark queries with expected keyword targets and ground-truth metadata.

## 3. Data Privacy & Confidentiality Notice
All documents included in this submission package are synthetic, unclassified, and specifically authored for academic demonstration and research purposes. No proprietary, trade-secret, or confidential OEM/Tier-1 automotive code or specifications are contained in these files.

## 4. Instructions for Using Custom Documents
To ingest your own AUTOSAR High-Level Design specifications:
1. Launch the Streamlit application (`http://localhost:8501`).
2. Navigate to **Documents** page (`2_Documents.py`).
3. Select an active project or create a new project.
4. Drag and drop any standard text-searchable PDF document.
5. PyMuPDF will extract text, chunk content, generate embeddings, and store records in SQLite and ChromaDB automatically.
