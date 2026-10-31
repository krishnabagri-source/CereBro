# AdaptIQ — Universal Adaptive AI Tutor (CereBro)

AdaptIQ is an intelligent, subject-independent adaptive learning platform designed for personalized exam preparation and mastery-based instruction.

The application features:
- A responsive React + TypeScript + Vite + TailwindCSS frontend (located in `/frontend` as well as root).
- A modular, universal Python + FastAPI + SQLAlchemy + SQLite backend with an explainable adaptive learning engine and Google Gemini AI tutoring integration (located in `/backend`).

---

## Architecture Overview

```
CereBro/
├── frontend/                     # Dedicated frontend workspace
│   ├── src/
│   │   ├── App.tsx               # Main application shell & UI pages
│   │   ├── api.ts                # Full REST API client
│   │   ├── engine.ts             # Domain models & fallback logic
│   │   └── style.css             # Design tokens & styling
│   ├── package.json
│   └── vite.config.ts            # Proxies /api to FastAPI backend (port 8000)
├── backend/                      # Universal Adaptive Backend
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint & router mounts
│   │   ├── config.py             # Configuration & environment settings
│   │   ├── database.py           # SQLite connection & session management
│   │   ├── models/               # SQLAlchemy models (Learner, ConceptMastery, Attempt, Assessment)
│   │   ├── schemas/              # Pydantic schemas (Subject, Learner, Learning, Assessment, etc.)
│   │   ├── routers/              # REST API endpoints (subjects, learners, assessments, learning, etc.)
│   │   ├── services/             # Adaptive engine, Subject loader, Learner service, Gemini AI tutor
│   │   └── data/subjects/        # Declarative subject definitions (Algebra, Python, Security, Physics)
│   ├── tests/                    # 23 automated pytest tests
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── package.json                  # Root runner scripts
└── README.md
```

---

## Quick Start

### 1. Requirements
- **Node.js**: 20+
- **Python**: 3.10+
- **npm**

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

*(Optional)* Configure Gemini AI Tutor in `backend/.env`:
```bash
cp .env.example .env
# Edit .env and supply your GEMINI_API_KEY
```
*Note: If no API key is provided, the backend automatically uses verified question-bank content and deterministic pedagogical templates without crashing.*

### 3. Run the Full Application
From the root directory:
```bash
npm run dev
```
This runs concurrently:
- **FastAPI backend** at `http://localhost:8000` (API Docs at `http://localhost:8000/docs`)
- **Vite frontend** at `http://localhost:5173`

Or run them individually in separate terminals:
```bash
# Terminal 1: Backend
npm run dev:backend

# Terminal 2: Frontend
npm run dev:client
# (Or cd frontend && npm run dev)
```

---

## Core Features & Functionality

### 1. Subject Independence
Subject curricula are declared as structured JSON documents under `backend/app/data/subjects/`.
Shipped initial subjects:
- **Mathematics**: Algebra
- **Programming**: Python Fundamentals
- **Cybersecurity**: Web Security Fundamentals
- **Science**: Physics: Electricity (Demonstrating domain generalization)

Adding any new subject (e.g. Data Structures, Chemistry, AI/ML) only requires adding a JSON file. The adaptive engine requires **zero code changes** to support new domains.

### 2. Explainable Adaptive Learner Model
- **Concept-wise mastery (0–100)**: Tracked per learner and concept.
- **Bounded Evidence Updates**: Uses an Exponential Moving Average (70% prior mastery, 30% new evidence) capped to a maximum change of ±18 points per answer.
- **Safety guarantee**: A single correct answer never jumps to 100% mastery.
- **Difficulty adaptation**: Tracks consecutive successes to step question difficulty between Beginner (1), Intermediate (2), and Advanced (3).

### 3. Adaptive Recommendation & Roadmap Engine
- **Prerequisite Enforcement**: Concepts are only unlocked when all prerequisites attain ≥60% mastery.
- **Personalized Prioritization**: Students with different learning profiles studying the same subject receive different recommendations (e.g., struggling students are directed to weak foundational concepts, while advanced students unlock next-tier topics).
- **Spaced-Repetition Scheduling**: Missed concepts return for review tomorrow (+1 day); mastered concepts schedule revisions across 2 to 7 days.

### 4. Gemini AI Tutor Service
- **Context-Aware Explanations**: Explains concepts tailored to the student's mastery level and difficulty tier.
- **Progressive Hints**: Provides clues without revealing answers directly.
- **Misconception Detection**: Evaluates student reasoning and mistakes to identify common misconceptions (e.g., confusing assignment `=` with equality `==`, or operating on only one side of an algebraic equation).
- **Graceful Fallback**: If offline or unconfigured, the AI service uses verified question bank and pedagogical templates without error.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/subjects` | List all dynamic subjects |
| `GET` | `/api/subjects/{id}` | Subject details, concepts, and diagnostics |
| `GET` | `/api/subjects/{id}/concepts` | Concepts and prerequisite graph |
| `POST` | `/api/learners` | Create a new learner profile |
| `GET` | `/api/learners` | List all learners |
| `GET` | `/api/learners/{id}/progress` | Learner mastery and learning gaps |
| `POST` | `/api/assessments/start` | Start diagnostic or practice assessment |
| `POST` | `/api/assessments/{id}/submit` | Submit answers and update concept mastery |
| `GET` | `/api/learners/{id}/recommendations` | Personalized next step recommendation |
| `GET` | `/api/learners/{id}/roadmap` | Prerequisite-aware roadmap with statuses |
| `POST` | `/api/learning/ask` | AI Tutor doubt, explanation, or hint |
| `POST` | `/api/learning/submit-answer` | Practice answer submission & misconception diagnosis |
| `GET` | `/api/learners/{id}/revisions` | Spaced-repetition items due now & upcoming |
| `GET` | `/api/state` | Legacy frontend state compatibility |
| `PUT` | `/api/selection` | Legacy frontend learner/subject switch |

---

## Automated Verification

Run the automated test suite:
```bash
npm run test:backend
# or: cd backend && python -m pytest tests -v
```
All 23 unit and integration tests verify:
- Single correct answer does not result in 100% mastery.
- Step change capping (±18 points maximum).
- Prerequisite unlocking logic.
- Differentiated recommendations for different student profiles.
- Diagnostic assessment start and submission.
- Practice answer grading and misconception analysis.
- AI Tutor fallback resilience without API keys.
- SQLite persistence across server restarts.
- Legacy frontend endpoint compatibility.
