# AutoSec TARA Assistant

Automotive Cybersecurity Threat Analysis and Risk Assessment platform aligned with **ISO/SAE 21434** and **UNECE R155/R156**.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Streamlit dashboard
cd frontend
streamlit run app.py

# 3. Run the FastAPI backend (separate terminal)
uvicorn app.api.main:app --reload

# 4. Run tests
pytest tests/ -v
```

## Docker

```bash
docker-compose up --build
```

- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Architecture

| Layer       | Technology           | Purpose                                    |
|-------------|----------------------|--------------------------------------------|
| Frontend    | Streamlit            | Thales-styled interactive TARA workbench   |
| API         | FastAPI              | REST endpoints for enterprise integration  |
| Database    | SQLite + SQLAlchemy  | Audit trail and threat persistence         |
| Vector DB   | ChromaDB             | Semantic retrieval of threat patterns       |
| Embeddings  | BGE (bge-small-en)   | Local embedding model for RAG pipeline     |
| Risk Engine | Pure Python          | Deterministic ISO 21434 scoring (no LLM)   |

## Project Structure

```
tara-assistant/
├── app/
│   ├── core/           # Config, risk engine, schemas, prompts
│   ├── services/       # Ingestion, RAG, TARA generator, graph, export
│   ├── database/       # SQLAlchemy ORM models and session
│   └── api/            # FastAPI REST endpoints
├── frontend/           # Streamlit dashboard with Thales UI
├── tests/              # pytest unit and integration tests
├── data/               # SQLite DB and raw input files
├── vectorstore/        # ChromaDB persistent storage
└── sample_data/        # Pre-loaded vehicle architecture specs
```
