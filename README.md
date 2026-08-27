# JobTrack AI 🚀
### Intelligent Job Application Tracker & Resume Matcher

JobTrack AI is a full-stack, AI-powered platform designed to streamline job hunt workflows. It allows job seekers to track applications across customizable Kanban pipeline stages, parse resumes (PDF/DOCX), and compute intelligent match scores against job descriptions using NLP and semantic scoring.

---

## 🌟 Key Features

- 🔐 **Secure Authentication & RBAC**: JWT-based access & refresh token lifecycle with bcrypt password hashing.
- 📋 **Application Pipeline Tracking**: Track job applications through stages (Applied, Interviewing, Offered, Rejected).
- 📄 **Smart Resume Parsing**: Extracts structured text and skills from PDF and DOCX files.
- 🤖 **AI Match & Scoring Engine**: Compares resume contents with job descriptions to highlight match percentages and skill gaps.
- ⚡ **High-Performance API**: Built with FastAPI, SQLAlchemy ORM, and Pydantic v2 data validation.
- 🧪 **Thoroughly Tested**: Unit and integration test coverage with Pytest.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0
- **Security**: Passlib (Bcrypt), Python-Jose (JWT), Python-Multipart
- **Document Parsing & Data**: PyPDF, Python-docx, Pandas
- **Database**: MySQL / PostgreSQL / SQLite
- **Testing**: Pytest, Pytest-asyncio, HTTPX

---

## 📁 Project Structure

```text
Job_Track_AI/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Register, Login, Refresh, Me endpoints
│   │       │   └── health.py        # System and DB health check
│   │       └── api_router.py        # Central v1 API router
│   ├── core/
│   │   ├── nlp/                     # NLP & AI matching modules
│   │   └── security.py              # JWT token and password hashing utilities
│   ├── crud/
│   │   └── crud_user.py             # User database operations
│   ├── db/
│   │   ├── base.py                  # Declarative base
│   │   └── session.py               # SQLAlchemy database session setup
│   ├── models/
│   │   └── user.py                  # User SQLAlchemy database model
│   ├── schemas/
│   │   ├── token.py                 # JWT token schemas
│   │   └── user.py                  # User request/response schemas
│   ├── services/                    # Business logic & parsing services
│   ├── config.py                    # App configuration & settings
│   └── main.py                      # FastAPI application entry point
├── tests/
│   ├── unit/                        # Unit tests (e.g. security utils)
│   ├── integration/                 # Integration tests (e.g. auth API, health check)
│   └── conftest.py                  # Pytest fixtures & test DB setup
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── pytest.ini                       # Pytest configuration
├── requirements.txt                 # Production dependencies
└── requirements-dev.txt             # Development & testing dependencies
```

---

## 🚦 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/svijay2026/JobTrack-AI.git
cd JobTrack-AI
```

### 3. Setup Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and adjust the variables if needed:
```bash
cp .env.example .env
```

### 6. Run the Application
```bash
uvicorn app.main:app --reload --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser for the interactive Swagger API documentation.

---

## 🧪 Running Tests

Execute the automated test suite with:
```bash
pytest
```

---

## 🗺️ Roadmap

- [x] **Phase 1**: Base Architecture, Database Configuration & JWT Authentication System.
- [x] **Phase 2**: Resume Upload & Parsing Engine (PDF/DOCX extraction).
- [x] **Phase 3**: Job Application Management & Pipeline Tracking (CRUD + Status updates).
- [ ] **Phase 4**: AI Resume-to-Job Matching & Keyword Analysis.
- [ ] **Phase 5**: Web Frontend Dashboard & Cloud Deployment.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
