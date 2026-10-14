# 🛡️ AutoSec TARA Assistant
### Automotive Cybersecurity Threat Analysis & Risk Assessment Platform
**Aligned with ISO/SAE 21434, UNECE R155 (CSMS), and UNECE R156 (SUMS)**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.26.0+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3.0+-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![ISO/SAE 21434](https://img.shields.io/badge/Standard-ISO%2FSAE%2021434-success.svg)](https://www.iso.org/standard/70918.html)
[![UNECE R155](https://img.shields.io/badge/Regulation-UNECE%20R155%20%2F%20R156-green.svg)](https://unece.org)
[![Tests Passing](https://img.shields.io/badge/Tests-83%20Passed-brightgreen.svg)](https://github.com/Pavankumargr2004/TARA)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Executive Overview

**AutoSec TARA Assistant** is an enterprise-grade automotive cybersecurity workbench engineered to automate Threat Analysis and Risk Assessment (TARA) throughout the vehicle development lifecycle. Built for OEM cybersecurity engineers, systems architects, and regulatory auditors, the platform bridges regulatory compliance (**ISO/SAE 21434**, **UNECE R155/R156**, **ISO 26262 ASIL-D**) with advanced automated threat intelligence, machine learning analytics, and enterprise engineering workflows.

---

## 🚀 Key Platform Capabilities

### 1. 🤖 Dual Machine Learning Threat & Risk Engine (`app/services/ml_model.py`)
- **STRIDE Threat Classifier**: Multi-class `RandomForestClassifier` trained on multi-attribute automotive vectors (`elapsed_time`, `expertise`, `knowledge`, `window`, `equipment`, `impact_score`), achieving **97.2% classification accuracy** and **0.972 weighted F1-score**.
- **ISO Risk Level Predictor**: `GradientBoostingClassifier` predicting regulatory ISO 21434 Risk Levels (1 through 5) with **97.2% accuracy** and **0.971 weighted F1-score**.
- **5-Fold Cross-Validation**: Validated using 5-fold stratified cross-validation for high generalizability across novel vehicle topologies.
- **Explainable AI (XAI)**: Feature importance analysis determining that **Attacker Expertise (31.7%)** and **Impact Score (25.3%)** are the primary drivers of threat severity.
- **Interactive ML Analytics & EDA Workbench (Tab 7)**: Live metrics cards, 6x6 STRIDE and 5x5 Risk confusion matrices, feature importance charts, and real-time "What-If" prediction playground.

### 2. 📐 Deterministic ISO/SAE 21434 Risk Engine (`app/core/risk_engine.py`)
- **Zero LLM Non-Determinism**: Formal mathematical implementation of ISO/SAE 21434 Clause 15.6 Attack Potential and Clause 15.5 Impact rating.
- **Attack Feasibility Scoring**: Calculated across five standardized factors:
  - *Elapsed Time* (`< 1 Month`, `<= 3 Months`, `<= 6 Months`, `> 6 Months`)
  - *Specialist Expertise* (`Layman`, `Proficient`, `Expert`, `Multiple Experts`)
  - *Knowledge of the Item* (`Public`, `Restricted`, `Confidential`, `Strictly Confidential`)
  - *Window of Opportunity* (`Unrestricted`, `Easy`, `Moderate`, `Difficult`)
  - *Equipment* (`Standard`, `Specialized`, `Bespoke`)
- **Annex H Risk Matrix Determination**: Maps combined Impact (1-4) and Feasibility (`High`, `Medium`, `Low`, `Very Low`) to ISO Risk Levels **1 to 5**.

### 3. 🔌 Automotive Architecture Parsers (`app/services/autosar_dbc_parser.py`)
- **AUTOSAR System Description (.ARXML)**: Automated XML extraction of ECU instances, zonal domain partitions, communication channels (SOME/IP, Automotive Ethernet, CAN-FD), and trust boundary definitions.
- **CAN Network Database (.DBC)**: Automated regex parsing of network nodes (`BU_:`), CAN messages (`BO_`), signal matrices (`SG_`), DLC parameters, and SecOC CMAC validation tags.
- **Pre-Loaded Architecture Datasets**: 12 diverse sample datasets in `sample_data/` covering ADAS, Android Automotive OS (AAOS), Digital Key 3.0, C-V2X, BMS, Brake-by-Wire, and CCS DC Fast Charging.

### 4. 🏢 Enterprise ALM / PLM Synchronization (`app/services/alm_sync_service.py`)
- **Atlassian Jira REST API**: Formats and synchronizes TARA findings and Cybersecurity Requirements (CSR) directly into Jira Task/Bug tickets with ISO 21434 labels and audit tracking.
- **Jama Connect REST API**: Direct mapping of CSR items into standard Automotive Requirements Specifications for traceability against ISO 26262 and ASPICE processes.

### 5. 🔐 OAuth2 Authentication & Role-Based Access Control (RBAC) (`app/core/auth.py`)
- Standardized OAuth2 Password Bearer flow with HS256 JWT tokens.
- Four distinct enterprise roles with enforced authorization:
  - **Lead Security Auditor**: Full administrative access, audit trail approval, regulatory export.
  - **Cybersecurity Engineer**: Threat creation, TARA scoring, mitigation assignment, ALM sync.
  - **System Architect**: Architecture file ingestion, ECU topology management, trust boundary definition.
  - **Guest Viewer**: Read-only access to TARA matrices, graphs, and compliance dashboards.

---

## 🏛️ System Architecture

```
                                  AutoSec TARA Assistant
                                     System Topology
                                     
   +---------------------------------------------------------------------------------+
   |                                PRESENTATION LAYER                               |
   |   Streamlit Interactive Dashboard (Port 8501) | Orchid Cyber Theme              |
   |   [Tab 1] Ingestion       | [Tab 2] Attack Graph  | [Tab 3] TARA Matrix         |
   |   [Tab 4] What-If Sim     | [Tab 5] Audit Review  | [Tab 6] Compliance Export   |
   |                           | [Tab 7] ML Analytics & EDA                          |
   +---------------------------------------+-----------------------------------------+
                                           |
                                           v
   +---------------------------------------------------------------------------------+
   |                               APPLICATION API LAYER                             |
   |   FastAPI REST Engine (Port 8000) | OAuth2 JWT Bearer Tokens | RBAC             |
   |   /api/v1/auth/*     /api/v1/threats/*     /api/v1/audit/*     /api/v1/alm/*    |
   +---------------------------------------+-----------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
   +----------------------------------+          +----------------------------------+
   |        ANALYTICS & ENGINES       |          |      INGESTION & PERSISTENCE     |
   | - Scikit-Learn ML Pipeline       |          | - AUTOSAR ARXML & CAN DBC Parser |
   |   (RandomForest + GradientBoost) |          | - LangChain Document Ingestor    |
   | - Deterministic ISO 21434 Engine |          | - SQLAlchemy ORM + SQLite DB     |
   | - NetworkX & PyVis Graph Builder |          | - ChromaDB Vectorstore           |
   | - ReportLab PDF & CSV Exporters  |          | - Jira & Jama REST Sync Services |
   +----------------------------------+          +----------------------------------+
```

---

## 📂 Project Structure

```
tara-assistant/
├── .github/
│   └── workflows/
│       └── ci.yml                      # GitHub Actions CI workflow (linting + pytest)
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py                     # FastAPI REST server & routing
│   ├── core/
│   │   ├── auth.py                     # OAuth2 JWT & Role-Based Access Control (RBAC)
│   │   ├── config.py                   # Pydantic-settings configuration
│   │   ├── prompts.py                  # Few-shot STRIDE & MITRE prompt templates
│   │   ├── risk_engine.py              # Pure deterministic ISO/SAE 21434 scoring engine
│   │   └── schemas.py                  # Pydantic data contracts (ThreatScenario, TrustBoundary)
│   ├── database/
│   │   ├── models.py                   # SQLAlchemy ORM models (Threat, ReviewAudit, User)
│   │   └── session.py                  # Database engine and session factory
│   └── services/
│       ├── alm_sync_service.py         # Jira & Jama Connect REST synchronization
│       ├── autosar_dbc_parser.py       # AUTOSAR ARXML & CAN DBC topology parsers
│       ├── export_service.py           # ReportLab PDF & CSV compliance exporters
│       ├── graph_builder.py            # NetworkX & PyVis multi-hop attack graphs
│       ├── ingestion.py                # LangChain multi-format document chunking
│       ├── ml_model.py                 # Scikit-Learn RandomForest & GradientBoosting pipeline
│       ├── rag_pipeline.py             # ChromaDB vector retrieval with BGE embeddings
│       └── tara_generator.py           # TARA automated threat synthesis
├── frontend/
│   └── app.py                          # Streamlit 7-Tab Workbench (Thales/Orchid design)
├── sample_data/                        # 12 Pre-loaded vehicle architecture specifications
│   ├── adas_autonomous_driving_spec.json
│   ├── bms_battery_management_system.dbc
│   ├── brake_by_wire_chassis_control.dbc
│   ├── central_gateway_security_zone.arxml
│   ├── digital_key_nfc_ble_uwb.json
│   ├── ev_fast_charging_iso15118_ccs.txt
│   ├── ev_powertrain_battery_spec.dbc
│   ├── ivi_infotainment_android_automotive.json
│   ├── ota_flashing_firmware_update.txt
│   ├── telematics_gateway_spec.txt
│   ├── v2x_c_v2x_dsrc_communication.json
│   └── zone_architecture_arxml_spec.arxml
├── tests/                              # 13 automated test suites (83 tests)
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_export_service.py
│   ├── test_graph_builder.py
│   ├── test_ingestion.py
│   ├── test_iso21434_compliance.py
│   ├── test_ml_model.py
│   ├── test_production_features.py
│   ├── test_prompts.py
│   ├── test_risk_engine.py
│   ├── test_sample_data_integrity.py
│   └── test_schemas.py
├── data/
│   ├── tara.db                         # SQLite audit and threat database
│   └── threat_training_data.csv        # ISO 21434 synthetic ML training dataset
├── docker-compose.yml                  # Local development container orchestration
├── docker-compose.prod.yml             # Production container orchestration
├── Dockerfile                          # Optimized multi-stage container build
├── requirements.txt                    # Project Python dependencies
├── AutoSec_TARA_Assistant_Project_Report.pdf      # Complete 8-page Technical Project Report
└── AutoSec_TARA_Assistant_Presentation_Guide.pdf # 10-slide Executive Presentation Guide
```

---

## ⚡ Quick Start Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git
- (Optional) Docker and Docker Compose

### 1. Local Python Setup

```bash
# 1. Clone repository and navigate into project directory
git clone https://github.com/Pavankumargr2004/TARA.git
cd TARA/tara-assistant

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Streamlit Interactive Workbench
streamlit run frontend/app.py --server.port 8501

# 5. Start the FastAPI Enterprise REST Server (in a separate terminal)
uvicorn app.api.main:app --reload --port 8000
```

- **Streamlit Workbench**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **FastAPI Alternative Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2. Docker Deployment

To launch the complete containerized stack:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background (detached mode)
docker-compose up -d --build

# Stop the containers
docker-compose down
```

---

## 🔑 Default User Accounts (RBAC)

The system automatically initializes 4 pre-configured enterprise user accounts with distinct role privileges:

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `admin` | `Admin@123` | **Lead Security Auditor** | Full system control, Threat approval/rejection, ALM sync, PDF export |
| `engineer` | `Eng@123` | **Cybersecurity Engineer** | Threat modeling, Risk scoring, Mitigation recommendations, Jira sync |
| `architect` | `Arch@123` | **System Architect** | ARXML & DBC file ingestion, Topology definition, Trust boundary mapping |
| `viewer` | `Viewer@123` | **Guest Viewer** | Read-only inspection of TARA matrix, attack graphs, and ML analytics |

---

## 🧪 Test Automation & Quality Gates

The project maintains **13 automated test suites** encompassing **83 unit and integration tests** with a **100% pass rate**:

```bash
# Run the complete test suite
pytest tests/ -v

# Run targeted ML test suite
pytest tests/test_ml_model.py -v

# Run with test coverage report
pytest --cov=app tests/
```

### Test Suite Summary:
- [`tests/test_ml_model.py`](file:///f:/TARA/tara-assistant/tests/test_ml_model.py): 21 tests verifying RandomForest STRIDE classifier, GradientBoosting risk predictor, 5-fold CV, confusion matrix dimensions, and feature importance.
- [`tests/test_production_features.py`](file:///f:/TARA/tara-assistant/tests/test_production_features.py): 9 tests covering OAuth2 password hashing, JWT encoding/decoding, RBAC endpoints, and Jira/Jama ALM service payloads.
- [`tests/test_iso21434_compliance.py`](file:///f:/TARA/tara-assistant/tests/test_iso21434_compliance.py): 5 tests validating Annex H risk matrix, attack potential factor thresholds, and safety critical hazard scoring.
- [`tests/test_ingestion.py`](file:///f:/TARA/tara-assistant/tests/test_ingestion.py): 8 tests testing document chunking across JSON, DBC, ARXML, and TXT specifications.
- [`tests/test_sample_data_integrity.py`](file:///f:/TARA/tara-assistant/tests/test_sample_data_integrity.py): 5 tests validating syntax integrity for all 12 pre-loaded vehicle architecture specifications.
- [`tests/test_database.py`](file:///f:/TARA/tara-assistant/tests/test_database.py): 4 tests for SQLAlchemy ORM models, session transactions, and audit trail records.
- [`tests/test_export_service.py`](file:///f:/TARA/tara-assistant/tests/test_export_service.py): 3 tests verifying ReportLab PDF generation and CSV export.
- [`tests/test_graph_builder.py`](file:///f:/TARA/tara-assistant/tests/test_graph_builder.py): 3 tests testing NetworkX directed attack graph generation.
- [`tests/test_risk_engine.py`](file:///f:/TARA/tara-assistant/tests/test_risk_engine.py): 11 tests verifying deterministic ISO 21434 scoring functions.
- [`tests/test_api.py`](file:///f:/TARA/tara-assistant/tests/test_api.py): 4 tests covering FastAPI REST endpoints.
- [`tests/test_config.py`](file:///f:/TARA/tara-assistant/tests/test_config.py): 5 tests validating application settings and paths.
- [`tests/test_schemas.py`](file:///f:/TARA/tara-assistant/tests/test_schemas.py): 3 tests validating Pydantic models.
- [`tests/test_prompts.py`](file:///f:/TARA/tara-assistant/tests/test_prompts.py): 2 tests verifying prompt templates.

---

## 📑 Executive Deliverables & Publications

The repository includes publication-ready technical reports generated by the built-in ReportLab engine:

1. **[`AutoSec_TARA_Assistant_Project_Report.pdf`](file:///f:/TARA/tara-assistant/AutoSec_TARA_Assistant_Project_Report.pdf)**
   - Comprehensive **8-page formal technical project report**.
   - Includes Executive Summary, System Architecture, ISO/SAE 21434 methodology, ML evaluation metrics, test results, and compliance certification summary.
2. **[`AutoSec_TARA_Assistant_Presentation_Guide.pdf`](file:///f:/TARA/tara-assistant/AutoSec_TARA_Assistant_Presentation_Guide.pdf)**
   - Professional **10-slide executive presentation guide** with slide-by-slide speaker notes, time allocations, and live demonstration scripts.

---

## 📜 Regulatory Standards Alignment

| Standard / Regulation | Clause / Section | Platform Implementation |
|-----------------------|------------------|-------------------------|
| **ISO/SAE 21434** | Clause 9: Item Definition | Automated ECU & bus extraction from ARXML/DBC specs |
| **ISO/SAE 21434** | Clause 15.3: Threat Scenarios | STRIDE classification & MITRE ATT&CK for ICS mapping |
| **ISO/SAE 21434** | Clause 15.5: Impact Rating | Multi-dimensional scoring across Safety, Financial, Operational, Privacy |
| **ISO/SAE 21434** | Clause 15.6: Attack Feasibility | 5-factor deterministic attack potential evaluation |
| **ISO/SAE 21434** | Clause 15.7: Risk Determination | Standard Annex H Risk Matrix lookup (Levels 1 to 5) |
| **UNECE R155** | Section 7.2: CSMS | Comprehensive audit logging, review trails, and mitigation tracking |
| **UNECE R156** | Section 7.1: SUMS | Secure boot, dual-bank A/B flashing, and rollback prevention controls |
| **ISO 26262** | Part 3 / Part 4 | Safety goal impact correlation for ASIL-B and ASIL-D critical actuators |

---

## 📄 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
