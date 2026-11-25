# CereBro — AdaptIQ Universal Adaptive AI Tutor

A full-stack adaptive learning platform with a **FastAPI Python backend** and **React + Vite + TypeScript frontend**.

---

## Project Structure

```
CereBro/
├── frontend/          ← React + Vite + TailwindCSS frontend (port 5173)
│   └── src/
│       ├── App.tsx    ← Main UI component
│       ├── api.ts     ← API client (proxies to backend)
│       └── engine.ts  ← Local subject data & logic
├── backend/           ← FastAPI Python backend (port 8000)
│   ├── app/
│   │   ├── main.py        ← FastAPI entrypoint
│   │   ├── config.py      ← Settings & env vars
│   │   ├── database.py    ← SQLite + SQLAlchemy
│   │   ├── models/        ← ORM models (Learner, ConceptMastery, Attempt)
│   │   ├── schemas/       ← Pydantic schemas
│   │   ├── routers/       ← API endpoints
│   │   │   ├── state.py          ← /api/state, /api/selection, /api/diagnostic, /api/practice
│   │   │   ├── subjects.py       ← /api/subjects
│   │   │   ├── learners.py       ← /api/learners
│   │   │   ├── assessments.py    ← /api/assessments
│   │   │   ├── learning.py       ← /api/learning/ask, /api/learning/submit-answer
│   │   │   ├── recommendations.py← /api/learners/{id}/recommendations
│   │   │   ├── roadmap.py        ← /api/learners/{id}/roadmap
│   │   │   └── revisions.py      ← /api/learners/{id}/revisions
│   │   ├── services/      ← Business logic
│   │   │   ├── adaptive_engine.py ← Mastery algorithm, spaced repetition
│   │   │   ├── ai_tutor.py       ← Gemini AI integration with fallback
│   │   │   ├── learner_service.py ← Learner CRUD + mastery updates
│   │   │   └── subject_service.py ← Subject JSON loader
│   │   └── data/subjects/ ← Subject JSON files (algebra, python, physics, security)
│   ├── .env            ← Add GEMINI_API_KEY here
│   └── requirements.txt
├── start.ps1          ← One-click startup script (Windows PowerShell)
└── README.md
```

---

## Quick Start

### Option 1 — One-click (PowerShell)

```powershell
.\start.ps1
```

This opens two terminal windows: one for the backend, one for the frontend.

### Option 2 — Manual

**Terminal 1 — Backend:**
```powershell
cd backend
C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```powershell
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/state` | GET | Full app state (learners + subjects) |
| `/api/selection` | PUT | Switch learner / subject |
| `/api/diagnostic` | POST | Submit diagnostic quiz |
| `/api/practice` | POST | Submit practice answer |
| `/api/subjects` | GET | List all subjects |
| `/api/subjects/{id}` | GET | Full subject with concepts |
| `/api/learners` | GET | List learners |
| `/api/learners/{id}/recommendations` | GET | Adaptive recommendation |
| `/api/learners/{id}/roadmap` | GET | Learning roadmap |
| `/api/learners/{id}/revisions` | GET | Spaced repetition schedule |
| `/api/learning/ask` | POST | AI tutor (Gemini or fallback) |
| `/api/learning/submit-answer` | POST | Submit practice with AI feedback |
| `/docs` | GET | Swagger UI |

---

## AI Tutor (Gemini)

Add your Gemini API key to `backend/.env`:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

Without a key, the AI tutor falls back to deterministic template responses — the app still works fully.

---

## Subjects Available

| Subject | Domain | Concepts |
|---------|--------|----------|
| Algebra | Mathematics | Expressions, Linear equations, Graphing lines |
| Python Fundamentals | Programming | Variables & types, Conditionals, Loops |
| Physics: Electricity | Science | Electric current, Potential difference, Ohm's Law |
| Web Security Fundamentals | Cybersecurity | HTTP & HTTPS, XSS, SQL Injection |
