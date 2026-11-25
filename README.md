# 🧠 CereBro — AdaptIQ Universal Adaptive AI Tutor

> **Learn smarter. Understand deeper. Improve continuously.**

CereBro is an AI-powered adaptive learning platform designed to make education more personalized and effective. Built with a **FastAPI Python backend** and a **React + Vite + TypeScript frontend**, it adapts in real time to each learner's performance.

Unlike conventional AI tutors that primarily answer questions, CereBro understands *how* a student learns — tracking conceptual understanding, identifying knowledge gaps, and adapting the learning experience accordingly.

Developed for the **Agentic AI Hackathon '26**.

---

## 💡 The Problem

Traditional learning systems provide standardized experiences despite students having different levels of understanding.

Getting an answer wrong doesn't mean the student lacks knowledge of the entire topic — they might have misunderstood one specific concept. Getting it right doesn't always demonstrate complete conceptual understanding either.

**CereBro bridges this gap by making learning adaptive rather than standardized.**

---

## ✨ Core Features

- **Diagnostic Assessment** — Evaluate the learner's existing knowledge before teaching
- **Adaptive Learning** — Personalize the experience based on individual performance
- **Concept-Level Mastery Tracking** — Track understanding at the individual concept level (0–100%)
- **Knowledge Gap Identification** — Identify topics requiring additional attention
- **Misconception Analysis** — Detect and explain the reasoning behind incorrect answers
- **Intelligent Questioning** — Target practice questions toward weaker concepts
- **Spaced Repetition** — Reinforce learning through scheduled revision (SM-2 inspired)
- **AI Tutor (Gemini)** — Ask questions, get explanations and hints in context
- **Multi-Subject Support** — Algebra, Python, Physics, Web Security (extensible via JSON)

---

## 🔄 Learning Workflow

```
Assess → Analyze → Track Mastery → Identify Gaps → Personalize → Practice → Improve
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4, Lucide React |
| Backend | Python 3.13, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2 |
| Database | SQLite (via SQLAlchemy ORM) |
| AI Integration | Google Gemini API (`gemini-1.5-flash`) with deterministic fallback |
| Dev Tooling | npm, concurrently, tsx |

---

## 🏗️ Project Structure

```
CereBro/
├── frontend/          ← React + Vite + TailwindCSS (port 5173)
│   └── src/
│       ├── App.tsx        ← Main UI component
│       ├── api.ts         ← API client (proxied to backend)
│       └── engine.ts      ← Local subject data & logic
├── backend/           ← FastAPI Python backend (port 8000)
│   ├── app/
│   │   ├── main.py        ← FastAPI entrypoint
│   │   ├── config.py      ← Settings & env config
│   │   ├── database.py    ← SQLite + SQLAlchemy setup
│   │   ├── models/        ← ORM models (Learner, ConceptMastery, Attempt)
│   │   ├── schemas/       ← Pydantic request/response schemas
│   │   ├── routers/       ← API route handlers
│   │   └── services/      ← Business logic (adaptive engine, AI tutor, learner service)
│   │       ├── adaptive_engine.py  ← Mastery algorithm, spaced repetition
│   │       ├── ai_tutor.py         ← Gemini AI integration
│   │       ├── learner_service.py  ← Learner CRUD + mastery updates
│   │       └── subject_service.py  ← Subject JSON loader
│   ├── data/subjects/ ← Subject JSON files (algebra, python, physics, security)
│   ├── .env           ← Add GEMINI_API_KEY here (never commit)
│   ├── .env.example   ← Template for environment variables
│   └── requirements.txt
├── server/            ← Legacy Express/TypeScript compatibility server
├── src/               ← Legacy root-level source (original frontend)
├── start.ps1          ← One-click Windows startup script
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v18+) and **npm**
- **Python 3.11+**
- **pip**

### 1. Clone the repository

```bash
git clone https://github.com/krishnabagri-source/CereBro.git
cd CereBro
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
```

### 3. Set up the Python backend

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your Gemini API key:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

> ⚠️ Never commit `.env` files or API keys to Git.

### 5. Run CereBro

**Option A — One-click (Windows PowerShell):**
```powershell
.\start.ps1
```

**Option B — Manual (two terminals):**

Terminal 1 — Backend:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 — Frontend:
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## 📡 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/state` | GET | Full app state (learners + subjects) |
| `/api/selection` | PUT | Switch active learner / subject |
| `/api/diagnostic` | POST | Submit diagnostic quiz answers |
| `/api/practice` | POST | Submit practice answer |
| `/api/subjects` | GET | List all subjects |
| `/api/subjects/{id}` | GET | Full subject with concepts |
| `/api/learners` | GET | List all learners |
| `/api/learners/{id}/recommendations` | GET | Adaptive concept recommendation |
| `/api/learners/{id}/roadmap` | GET | Full concept roadmap with mastery |
| `/api/learners/{id}/revisions` | GET | Spaced repetition revision schedule |
| `/api/learning/ask` | POST | Ask the AI tutor |
| `/api/learning/submit-answer` | POST | Submit practice with AI feedback |

> Interactive Swagger docs: **http://localhost:8000/docs**

---

## 📚 Subjects Available

| Subject | Domain | Concepts |
|---------|--------|----------|
| Algebra | Mathematics | Expressions & variables, Linear equations, Graphing lines |
| Python Fundamentals | Programming | Variables & types, Conditionals, Loops |
| Physics: Electricity | Science | Electric current, Potential difference, Ohm's Law & circuits |
| Web Security Fundamentals | Cybersecurity | HTTP & HTTPS, Cross-site scripting (XSS), SQL Injection |

---

## 🔮 Future Scope

- More advanced learner knowledge modeling
- Improved reasoning-based misconception detection
- Dynamic difficulty calibration
- Expanded subject and domain support
- Better concept relationship mapping
- Personalized revision scheduling
- Learning analytics and progress visualization

---

## 👥 Team

Built collaboratively by:

- **Krishna Bagri** — [GitHub](https://github.com/krishnabagri-source)

---

## 🏆 Hackathon

**Event:** Agentic AI Hackathon '26
**Organizer:** Product Space
**Date:** September 21, 2026

---

## 📌 Repository

[Explore CereBro on GitHub](https://github.com/krishnabagri-source/CereBro)

---

**CereBro — Because understanding matters more than just getting the answer right.** 🧠
