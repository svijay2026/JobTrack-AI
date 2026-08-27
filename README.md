# JobTrack AI 🚀
### Intelligent Job Application Tracker & AI Resume Matcher

JobTrack AI is a full-stack, AI-powered platform designed to streamline job hunt workflows. It allows job seekers to track applications across customizable Kanban pipeline stages, parse resumes (PDF/DOCX), and compute intelligent match scores against job descriptions using NLP, TF-IDF cosine semantic similarity, and skill gap detection.

---

## 🌟 Key Features

- 🔐 **Secure Authentication & RBAC**: JWT-based access & refresh token lifecycle with bcrypt password hashing.
- 📄 **Smart Resume Parsing**: Extracts clean text, contact details (Email, Phone, LinkedIn, GitHub), education, and 200+ technical/domain skills from PDF and DOCX files.
- 📋 **Application Pipeline Tracking**: Track job applications through Kanban stages (*Wishlist*, *Applied*, *Interviewing*, *Offered*, *Rejected*, *Accepted*, *Archived*).
- 📊 **Pipeline Analytics & Funnel Metrics**: Real-time conversion tracking (interview rates, offer rates, application totals).
- 🔍 **Search & Filtering**: Search applications by company, title, location, or filter by stage.
- 🤖 **AI Match & Scoring Engine**:
  - Multi-dimensional weighted match score (0 - 100%) combining Skill Overlap (50%), Semantic Relevance (35%), and Experience Alignment (15%).
  - Detailed breakdown of **Matching Skills** vs **Missing Skill Gaps**.
  - Actionable, personalized resume improvement recommendations tailored to the specific job post.
  - Supports matching against tracked jobs or ad-hoc pasted job descriptions.
  - Full match analysis history tracking.
- ⚡ **High-Performance API**: Built with FastAPI, SQLAlchemy ORM, and Pydantic v2 data validation.
- 🧪 **Thoroughly Tested**: Comprehensive suite of 46 automated unit and integration tests with Pytest (100% pass rate).

---

## 🛠️ Tech Stack

- **Backend Framework**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0
- **AI & NLP Engine**: TF-IDF Vectorizer, Cosine Semantic Similarity, Skill Taxonomy Matcher, Heuristic Experience Evaluator
- **Security & Auth**: Passlib (Bcrypt), Python-Jose (JWT), Python-Multipart, OAuth2 Bearer Tokens
- **Document Parsing & Extraction**: PyPDF, Python-docx, Regex Boundary Extractors
- **Database & Persistence**: MySQL / PostgreSQL / SQLite
- **Testing**: Pytest, Pytest-asyncio, HTTPX TestClient

---

## 📁 Project Structure

```text
Job_Track_AI/
├── app/
│   ├── api/
│   │   ├── deps.py                  # OAuth2 authentication & DB session dependencies
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Register, Login, Refresh, Me endpoints
│   │       │   ├── health.py        # System and DB health check
│   │       │   ├── resumes.py       # Resume Upload, Download, Parser, Primary selector
│   │       │   ├── jobs.py          # Job Application CRUD, Kanban status transitions & Stats
│   │       │   └── matching.py      # AI Resume-to-Job matching, scoring & analysis history
│   │       └── api_router.py        # Central v1 API router
│   ├── core/
│   │   ├── nlp/
│   │   │   └── matcher.py           # TF-IDF, Cosine Similarity, Skill Gap & Recommendation engine
│   │   └── security.py              # JWT token handling and Bcrypt password hashing
│   ├── crud/
│   │   ├── crud_user.py             # User DB operations
│   │   ├── crud_resume.py           # Resume DB operations & disk cleanup
│   │   ├── crud_job.py              # Job Application DB operations & analytics
│   │   └── crud_match.py            # AI Match Analysis DB operations
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy DeclarativeBase
│   │   └── session.py               # Database engine & connection pooling setup
│   ├── models/
│   │   ├── user.py                  # User SQLAlchemy model
│   │   ├── resume.py                # Resume SQLAlchemy model
│   │   ├── job.py                   # JobApplication SQLAlchemy model
│   │   └── match.py                 # MatchAnalysis SQLAlchemy model
│   ├── schemas/
│   │   ├── token.py                 # JWT token request/response schemas
│   │   ├── user.py                  # User schemas
│   │   ├── resume.py                # Resume upload & parsed data schemas
│   │   ├── job.py                   # Job application, status update & analytics schemas
│   │   └── match.py                 # AI match request, score breakdown & history schemas
│   ├── services/
│   │   ├── file_service.py          # Secure upload validation, storage & deletion
│   │   └── resume_parser.py         # Multi-format PDF/DOCX parser & skill extractor
│   ├── config.py                    # App configuration & environment settings
│   └── main.py                      # FastAPI application entry point
├── tests/
│   ├── conftest.py                  # Pytest fixtures & isolated SQLite test DB
│   ├── unit/
│   │   ├── test_security.py         # Password hashing & JWT token verification tests
│   │   ├── test_file_service.py     # Upload sanitization & size limit tests
│   │   ├── test_resume_parser.py    # Text, contact, education, skill extraction tests
│   │   └── test_matcher.py          # TF-IDF cosine similarity, skill gap & recommendation tests
│   └── integration/
│       ├── test_health.py           # Health check endpoint tests
│       ├── test_auth_api.py         # User registration, login, token refresh flows
│       ├── test_resumes_api.py      # Resume upload, retrieval, download, delete flows
│       ├── test_jobs_api.py         # Job creation, filtering, status patch & stats flows
│       └── test_matching_api.py     # AI match evaluation, history & cross-user isolation tests
├── .env.example                     # Environment configuration template
├── .gitignore                       # Git ignore rules
├── pytest.ini                       # Pytest configuration
├── requirements.txt                 # Production dependencies
└── requirements-dev.txt             # Development & testing dependencies
```

---

## 📡 API Endpoints Overview

### 🔐 Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new candidate account |
| `POST` | `/api/v1/auth/login` | Authenticate user and receive JWT access token |
| `POST` | `/api/v1/auth/refresh` | Refresh expired access tokens |
| `GET` | `/api/v1/auth/me` | Retrieve profile of the currently logged-in user |

### 📄 Resumes (`/api/v1/resumes`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/resumes/upload` | Upload PDF/DOCX resume & run automated parsing |
| `GET` | `/api/v1/resumes/` | List all resumes uploaded by the current user |
| `GET` | `/api/v1/resumes/primary` | Get the user's primary active resume |
| `GET` | `/api/v1/resumes/{id}` | Get detailed metadata and parsed skills of a resume |
| `GET` | `/api/v1/resumes/{id}/download` | Download raw original resume file |
| `PUT` | `/api/v1/resumes/{id}/primary` | Designate a resume as primary |
| `DELETE` | `/api/v1/resumes/{id}` | Delete resume record and remove file from storage |

### 📋 Job Applications (`/api/v1/jobs`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/jobs/` | Create a new job application (optional resume link) |
| `GET` | `/api/v1/jobs/` | List applications (with `status` filter, `search` keyword, pagination) |
| `GET` | `/api/v1/jobs/stats` | Pipeline conversion statistics & stage counts |
| `GET` | `/api/v1/jobs/{id}` | Get single job application details |
| `PUT` | `/api/v1/jobs/{id}` | Full update of job application record |
| `PATCH` | `/api/v1/jobs/{id}/status` | Kanban drag-and-drop quick stage transition |
| `DELETE` | `/api/v1/jobs/{id}` | Remove job application from tracker |

### 🤖 AI Matching & Scoring (`/api/v1/matching`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/matching/analyze` | Run AI match analysis between resume & job description |
| `GET` | `/api/v1/matching/history` | List previous match evaluations and scores |
| `GET` | `/api/v1/matching/{id}` | Retrieve detailed match report with skill gaps & tips |
| `DELETE` | `/api/v1/matching/{id}` | Delete a match analysis record |

### 🏥 System Health (`/api/v1/health`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check & database connection status |

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
*Currently **46/46 tests passing** across all unit and integration test suites.*

---

## 🗺️ Roadmap

- [x] **Phase 1**: Base Architecture, Database Configuration & JWT Authentication System.
- [x] **Phase 2**: Resume Upload & Parsing Engine (PDF/DOCX extraction & skill matching).
- [x] **Phase 3**: Job Application Management & Pipeline Tracking (Kanban statuses, search & analytics).
- [x] **Phase 4**: AI Resume-to-Job Matching & Keyword Analysis Engine.
- [ ] **Phase 5**: Web Frontend Dashboard & Cloud Deployment.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
