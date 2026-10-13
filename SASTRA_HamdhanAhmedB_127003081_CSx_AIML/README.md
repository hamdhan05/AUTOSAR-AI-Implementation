# AUTOSAR AI — High-Level Design Document Intelligence Platform

**Student Name**: Hamdhan Ahmed B  
**Register Number**: 127003081  
**Degree**: Bachelor of Technology (Computer Science & Engineering / AIML)  
**Institution**: SASTRA Deemed University, Thanjavur, Tamil Nadu, India  
**Repository**: [https://github.com/hamdhan05/AUTOSAR-AI-Implementation](https://github.com/hamdhan05/AUTOSAR-AI-Implementation)  

---

## 1. Project Directory Structure
```
SASTRA_HamdhanAhmedB_127003081_CSx_AIML/
├── Synopsis/                      # Academic synopsis (DOCX, PDF, and Abstract TXT)
├── Input_Data/                    # Sample HLD PDF specifications and 35-query benchmark set
├── Code/                          # Clean application source code (backend, frontend, tests)
├── Model_Prompts_Config/          # RAG system prompts and Ollama/embedding configuration
├── Evaluation_Results/            # 28/28 automated test reports, verification matrix, CSV results
├── Documentation/                 # Technical documentation, database design, API docs, viva Q&A
├── Video/                         # Spoken presentation script and live demo scene guides
├── Declarations/                  # Student declaration template and submission checklist
├── Presentation/                  # 8-slide PowerPoint (.pptx) and PDF presentation
├── README.md                      # Project root readme
├── LICENSE_OR_USAGE_NOTES.md      # Usage and academic licensing terms
└── requirements_and_file_manifest.txt # File manifest and environment requirements
```

## 2. Quick Execution Guide
1. **Navigate to Code**:
   ```powershell
   cd Code
   ```
2. **Set up Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. **Verify Ollama**:
   ```powershell
   ollama serve
   ```
4. **Launch Application**:
   ```powershell
   python run.py
   ```
   Open browser to `http://localhost:8501`.

5. **Run Automated Tests**:
   ```powershell
   python -m pytest tests/ -v
   ```
   Expected: `28 passed in ~27s` (100% pass rate).
