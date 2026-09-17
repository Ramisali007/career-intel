# CareerIntel ⚡

<div align="center">

### Production-Grade AI Career Intelligence, ATS Optimization & Deterministic CV Tailoring Platform

[![Next.js](https://img.shields.io/badge/Next.js-16.3-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2-blue?style=for-the-badge&logo=react&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <b>Transparent, evidence-backed CV analysis, multi-job description matching, ATS scoring, and factual resume optimization with zero hallucination.</b>
</p>

</div>

---

## 📌 Repository Description (Under 250 Chars)
> **Production-grade AI career intelligence platform. Evidence-backed CV analysis, deterministic ATS & Job Match scoring, multi-JD fit ranking, interactive visual diffs, and 100% ATS-safe LaTeX & DOCX export with zero qualification fabrication.**

---

## 🌟 Why CareerIntel?

Most "AI resume builders" are thin wrappers around generative models that silently fabricate candidate qualifications, invent employers, hallucinate skills, or arbitrarily boost arbitrary percentages. 

**CareerIntel** is an enterprise-ready Career Intelligence and ATS Optimization Platform built on strict engineering principles:
* 🛡️ **Zero Fabrication Guarantee**: Never fabricates skills, employment history, certifications, or degrees. If a skill isn't in your CV or verified profile, it's flagged as a gap, not invented.
* 🔎 **Evidence-Backed AI**: Every requirement match and recommendation cites exact excerpts from your CV with confidence indicators.
* 📐 **Deterministic Scoring Engine**: LLMs extract semantic evidence; a mathematical engine calculates transparent scores across 9 job match dimensions, 5 ATS metrics, and 8 CV quality criteria.
* 👤 **Human-in-the-Loop Control**: No silent modifications. Users explicitly review and approve or reject every proposed bullet point rewrite or keyword addition.
* 🔄 **Self-Repairing Claim Verifier**: Optimized content is fact-checked against original CV evidence prior to rendering. Unsupported claims are automatically eliminated.
* 📊 **Multi-JD Fit Comparison**: Compare your CV against 2 to 5 target Job Descriptions at once to detect shared industry requirements vs. unique company needs.
* 📄 **Pixel-Perfect ATS Safe Exports**: Generates 100% ATS-compliant PDFs (ReportLab / WeasyPrint) and native DOCX files across 6 professional templates, including the gold-standard Overleaf/LaTeX style.

---

## 📑 Table of Contents
- [Architecture & Workflow](#-architecture--workflow)
- [Core Features](#-core-features)
- [Scoring Dimensions](#-scoring-dimensions)
- [Available CV Export Templates](#-available-cv-export-templates)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Option A: Docker Compose (Recommended)](#option-a-docker-compose-recommended)
  - [Option B: Manual Local Setup](#option-b-manual-local-setup)
- [Environment Configuration](#-environment-configuration)
- [API Reference](#-api-reference)
- [Security & Architecture Standards](#-security--architecture-standards)
- [Running Tests](#-running-tests)
- [License](#-license)

---

## 🏗️ Architecture & Workflow

```
[ User Uploads CV (.pdf, .docx) & Target Job Description(s) ]
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                    STAGE 1: PARSING & EXTRACTION            │
 │ • PyMuPDF & python-docx extract raw text & layout metadata  │
 │ • LLM structured schema normalization (Experience, Skills)  │
 └─────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                    STAGE 2: EVIDENCE EXTRACTION             │
 │ • Semantic alignment linking CV passages to JD requirements │
 │ • Categorization: Must-Have, Preferred, Responsibilities    │
 └─────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │             STAGE 3: DETERMINISTIC SCORING ENGINE           │
 │ • Job Match Score (9 dimensions, weighted mathematically)   │
 │ • ATS Compatibility Score (Parsing, Structure, Keywords)    │
 │ • CV Quality Score (Impact, Clarity, Quantifiability)       │
 └─────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │          STAGE 4: RECOMMENDATIONS & HUMAN-IN-THE-LOOP       │
 │ • Actionable advice, keyword additions, impact bullet points│
 │ • Candidate reviews and Approves or Rejects suggestions    │
 └─────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │          STAGE 5: OPTIMIZATION & CLAIM VERIFICATION         │
 │ • CV Optimizer integrates only approved modifications       │
 │ • Claim Verifier checks factual integrity against source CV │
 │ • Self-Repair: Unsupported claims are pruned automatically  │
 └─────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │             STAGE 6: INDEPENDENT RESCORING & DIFF           │
 │ • Deterministic rescoring calculated on optimized version   │
 │ • Section-by-section and line-by-line Visual Diff view      │
 └─────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                  STAGE 7: ATS EXPORT ENGINE                 │
 │ • Render to PDF (ReportLab/WeasyPrint) & Word (.docx)       │
 │ • 6 ATS-optimized templates (LaTeX, Modern, Minimal, etc.) │
 └─────────────────────────────────────────────────────────────┘
```

---

## ✨ Core Features

### 1. Evidence-Backed CV & JD Parsing
* **Deep Document Ingestion**: Dual-engine parsing for PDF and DOCX documents with layout detection.
* **Intelligent Entity Structuring**: Normalizes varied candidate profiles into canonical sections (experience, education, skills matrix, projects, certifications, metrics).
* **Job Description Deconstruction**: Extracts hard requirements, soft requirements, toolsets, seniority level, and domain context.

### 2. Multi-JD Fit Matrix & Gap Analysis
* **Simultaneous Comparison**: Evaluate your resume against 2–5 job descriptions concurrently.
* **Cross-JD Synergy**: Automatically identifies common market requirements (present in $\ge 60\%$ of postings) versus company-specific one-offs.
* **4-Tier Skill Gap Classification**:
  1. `Already Have`: Strong evidence verified in CV ($\ge 70\%$ match score).
  2. `Need Better Evidence`: Partial or weakly demonstrated skills.
  3. `Missing`: Mandatory requirements missing from CV (highlights actionable learning goals).
  4. `Nice to Have`: Preferred/bonus credentials.

### 3. Transparent & Non-Hallucinatory Tailoring
* **Never Inactive or Silent**: AI never alters your CV behind your back.
* **Strict Evidence Sourcing**: Only sources from candidate's existing CV, verified Career Profile, or user-supplied additions.
* **Automatic Self-Repair**: If an LLM accidentally adds an unsupported claim during bullet optimization, the `CLAIM_VERIFIER_V1` engine detects it, rolls it back, and repairs the output.

### 4. Interactive Visual Diff & Version History
* **Side-by-Side Comparison**: Visually highlights added, modified, and removed bullets, summaries, and skill entries.
* **Full Audit Trail**: Maintains complete immutable snapshots of each version with instant rollback capabilities.

### 5. Resilient Dual-AI Routing
* **Zero Downtime Fallback**: Uses Google Gemini Flash (fast, high quota) as primary provider with automated circuit breaking to Groq (Qwen/Llama) if rate limits or network issues occur.
* **Zero Cost Operation**: Compatible with completely free tiers of Google AI Studio and Groq.

---

## 📊 Scoring Dimensions

Scores are computed **deterministically** by mathematical algorithms rather than arbitrary LLM guesses:

| Dimension Group | Metric | Weight | Description |
| :--- | :--- | :---: | :--- |
| **Job Match** | Required Skills | 25% | Direct matches for hard technical/role requirements |
| | Experience Relevance | 20% | Depth, role duration, and domain congruence |
| | Responsibilities | 15% | Alignment with core day-to-day deliverables |
| | Preferred Skills | 10% | Secondary and nice-to-have qualification matches |
| | Seniority Level | 8% | Scope of leadership and years in tier |
| | Education & Degrees | 7% | Degree level and field of study alignment |
| | Certifications | 5% | Industry licenses, vendor certifications |
| | Domain Knowledge | 5% | Vertical experience (FinTech, SaaS, Healthcare, etc.) |
| | Keyword Coverage | 5% | Semantic coverage of vital terminology |
| **ATS Compatibility** | Parsing Compatibility | 25% | Single-column legibility and parser compliance |
| | Section Structure | 25% | Standardized headers and logical hierarchy |
| | Keyword Density | 20% | Natural, non-stuffed keyword frequency |
| | Formatting Cleanliness| 15% | Standard font usage, clean margins, no graphics |
| | Text Readability | 15% | Bullet point length, clarity, and conciseness |
| **CV Quality** | Impact & Metrics | 15% | Quantified outcomes (e.g., "$1.2M saved", "35% faster") |
| | Clarity & Conciseness| 25% | Active voice, strong action verbs, no fluff |
| | Structural Logic | 25% | Chronological sequencing and section balance |
| | Writing & Grammar | 15% | Professional phrasing and tone |
| | Consistency | 20% | Uniform dates, bullet formats, and typography |

---

## 🎨 Available CV Export Templates

Every template is engineered to maintain **100% ATS readability** and parser compliance:

1. **Overleaf / LaTeX Classic**: The gold standard in tech, quantitative finance, and academia. Elegant Times New Roman typography, 2-column meta tables, categorized skill rows.
2. **ATS Classic Single-Column**: Maximum parser compatibility. Clean dividers, standard headings, tested on enterprise ATS parsers (Workday, Taleo, Greenhouse, Lever).
3. **Modern Professional**: Balanced whitespace with subtle navy/slate divider rules. Best for tech startups and consulting.
4. **Technical / Engineering**: Highlights tech stack matrices, GitHub/portfolio links, system architecture bullets, and quantitative deliverables.
5. **Minimalist Clean**: High density, restrained typography, maximum information efficiency for senior individual contributors.
6. **Executive Leadership**: Emphasizes strategic vision, executive summary, organizational scale, and P&L accountability.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16.3 (App Router) with React 19 & TypeScript
- **Styling**: Tailwind CSS v4 & PostCSS
- **Animations & Visuals**: Framer Motion, Lucide Icons, WebGL Shaders (OGL)
- **Design System**: Specular glass buttons, fluid gooey navigation, dark-mode canvas shaders

### Backend
- **Framework**: FastAPI (Python 3.12) with asynchronous ASGI worker
- **Database**: MongoDB 7.0 via Motor async driver & Beanie ODM
- **AI Integrations**: Google Generative AI (`google-generativeai`) & Groq (`groq`)
- **Document Processing**: PyMuPDF (`fitz`), `python-docx`, `Pillow`
- **PDF & Document Exporters**: ReportLab, WeasyPrint, `python-docx`
- **Security & Validation**: Pydantic v2, Python-Jose (JWT), Passlib / BCrypt, Magic byte inspection

---

## 📁 Project Structure

```
├── docker-compose.yml             # Container orchestration (MongoDB, Backend, Frontend)
├── backend/
│   ├── Dockerfile                 # Multi-stage Python 3.12 container
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment variables template
│   ├── app/
│   │   ├── main.py                # FastAPI entry point, middleware, lifecycle
│   │   ├── config.py              # Centralized Pydantic settings & scoring weights
│   │   ├── database.py            # MongoDB connection & Beanie initialization
│   │   ├── ai/                    # AI router, Gemini & Groq providers, prompt templates
│   │   ├── models/                # Beanie ODM models (User, Document, Analysis, etc.)
│   │   ├── routers/               # API endpoints (Auth, Documents, Analyses, Exports)
│   │   ├── security/              # JWT auth, rate limiting, file validation
│   │   ├── services/              # Pipeline orchestrator, scoring engine, CV exporter
│   │   └── utils/                 # Visual diff generator, text cleaners
│   └── tests/                     # Unit, integration, and golden test cases
├── frontend/
│   ├── Dockerfile                 # Next.js production build container
│   ├── package.json               # Node.js dependencies
│   └── src/
│       ├── app/
│       │   ├── page.tsx           # Landing page with interactive WebGL background
│       │   ├── (auth)/            # Login and registration pages
│       │   ├── dashboard/         # Aggregated overview & quick actions
│       │   ├── analyze/           # Single JD analysis & multi-JD matrix comparison
│       │   ├── analysis/[id]/     # Analysis results, scorecards, gap matrix & diff
│       │   ├── export/[id]/       # Template selector, PDF/DOCX live download
│       │   ├── history/           # Prior analysis sessions & audit management
│       │   └── profile/           # Career profile & master resume management
│       ├── components/
│       │   ├── ui/                # Lightfall, GooeyNav, SpecularButton, ScoreCard
│       │   └── analysis/          # Processing status tracker, RecommendationCard
│       └── lib/
│           ├── api.ts             # Centralized typed HTTP client with token handling
│           └── utils.ts           # Class merging and string helpers
```

---

## 🚀 Quick Start

### Prerequisites
- **Git**
- **Docker & Docker Compose** (Recommended) *OR*
- **Python 3.12+** & **Node.js 20+** with **MongoDB** installed locally.

---

### Option A: Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/career-intel.git
   cd career-intel
   ```

2. **Configure Environment Variables**:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Edit `backend/.env` to supply your free Gemini API Key or Groq API Key.*

3. **Start All Services**:
   ```bash
   docker-compose up --build -d
   ```

4. **Access the Application**:
   - **Frontend App**: [http://localhost:3000](http://localhost:3000)
   - **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Option B: Manual Local Setup

#### 1. Start MongoDB
Ensure MongoDB is running locally on port 27017, or start a lightweight container:
```bash
docker run -d -p 27017:27017 --name mongo-dev mongo:7
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Open .env and add your GEMINI_API_KEY / GROQ_API_KEY

uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔑 Environment Configuration

Key settings configurable in `backend/.env`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `AI CV Analyzer` | Application branding identifier |
| `ENVIRONMENT` | `development` | `development`, `staging`, or `production` |
| `SECRET_KEY` | *(random)* | JWT signature secret key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Session lifetime (24 hours) |
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection URI |
| `MONGODB_DB_NAME` | `cv_analyzer` | Database name |
| `GEMINI_API_KEY` | `""` | Free API key from [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_MODEL` | `gemini-flash-lite-latest` | Default primary Gemini model |
| `GROQ_API_KEY` | `""` | Free API key from [Groq Console](https://console.groq.com/) |
| `GROQ_MODEL` | `qwen/qwen3.8-27b` | Default Groq fallback model |
| `PRIMARY_AI_PROVIDER` | `gemini` | `gemini` or `groq` |
| `MAX_FILE_SIZE_MB` | `10` | Maximum uploaded CV file size |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

---

## 📡 API Reference

Interactive Swagger documentation is available at `/docs` when running the backend.

### Authentication
- `POST /api/v1/auth/register` — Create a new candidate account.
- `POST /api/v1/auth/login` — Obtain JWT bearer token.
- `GET /api/v1/auth/me` — Get current authenticated user profile.

### Documents & Ingestion
- `POST /api/v1/documents/upload` — Upload and parse a CV (.pdf or .docx).
- `GET /api/v1/documents/` — List uploaded candidate documents.
- `GET /api/v1/documents/{id}` — Retrieve extracted CV structured entities.

### Analyses & Matching
- `POST /api/v1/analyses/` — Initiate an asynchronous analysis session.
- `GET /api/v1/analyses/{id}` — Get analysis results, status, and scores.
- `GET /api/v1/analyses/{id}/gap-analysis` — Get 4-tier requirement breakdown.
- `POST /api/v1/analyses/{id}/optimize` — Apply approved recommendations and rescore.
- `POST /api/v1/analyses/multi-jd` — Compare CV against 2–5 job postings simultaneously.
- `GET /api/v1/analyses/diagnostics/system-health` — Operational metrics and provider status.

### Recommendations
- `GET /api/v1/recommendations/analysis/{id}` — Fetch all recommendations for an analysis.
- `POST /api/v1/recommendations/{id}/action` — Approve, reject, or edit a recommendation.

### CV Versions & Exporter
- `GET /api/v1/cv-versions/analysis/{id}` — List revision snapshots with score diffs.
- `POST /api/v1/cv-versions/{id}/rollback` — Revert back to an earlier version.
- `GET /api/v1/exports/templates` — List all 6 ATS-safe styling templates.
- `POST /api/v1/exports/{version_id}/pdf?template={template_id}` — Export ATS-safe PDF.
- `POST /api/v1/exports/{version_id}/docx?template={template_id}` — Export native Word document.

---

## 🔒 Security & Architecture Standards

1. **Strict File Validation**: Enforces MIME validation, file extension checks, path traversal protection (`os.path.basename` sanitation), and magic byte verification.
2. **Rate Limiting**: Sliding window rate-limiting middleware prevents resource starvation and abuse.
3. **Structured Observability**: Production JSON logging with unique request correlation IDs (`X-Request-ID`).
4. **Data Isolation**: All operations enforce strict user ownership validation on documents, analyses, and exported artifacts.
5. **Cascading Cleanups**: Deleting an analysis session automatically cascades to remove associated recommendation entities and version files.

---

## 🧪 Running Tests

To run the backend test suite:
```bash
cd backend
pytest tests/ -v
```

The test suite validates:
- Deterministic scoring engine calculations
- Semantic synonym normalization
- Document parser extraction fidelity
- Diffs generation and multi-format exports
- Data deletion, user authorization, and rollbacks

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
