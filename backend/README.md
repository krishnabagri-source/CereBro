# AdaptIQ — Universal Adaptive AI Tutor Backend

A modular, subject-independent adaptive learning backend built with Python, FastAPI, SQLAlchemy, and SQLite, powered by an explainable learner mastery engine and Google Gemini AI tutoring services.

## Architecture

- **Subject Independence**: Subject curricula are stored as declarative JSON configurations in `app/data/subjects/`. Adding a new subject (e.g. Physics, Chemistry, Biology, Data Structures) requires zero modifications to the adaptive learning engine.
- **Explainable Learner Model**: Concept-wise mastery tracked on a 0–100 scale using an Exponential Moving Average (EMA) evidence model with bounded step adjustments (max ±18 pts per attempt). A single correct answer never yields 100% mastery.
- **Adaptive Recommendation Engine**: Evaluates concept graphs and enforces prerequisite mastery thresholds (>=60%) before unlocking advanced topics. Differentiates learning paths for individual students.
- **Spaced-Repetition Scheduling**: Adjusts revision intervals dynamically based on learner mastery and outcome (missed concepts return tomorrow; mastered concepts return in up to 7 days).
- **Gemini AI Tutor**: Provides contextual concept explanations, progressive hints, adaptive practice question generation, and misconception detection. Automatically falls back gracefully to verified question-bank content when offline or unconfigured.

## Directory Structure

```
backend/
  app/
    config.py           # Configuration & environment settings
    database.py         # SQLAlchemy SQLite session management
    main.py             # FastAPI entrypoint, middleware, router mounts
    models/             # SQLAlchemy ORM models (Learner, Mastery, Attempt, Assessment)
    schemas/            # Pydantic validation schemas
    routers/            # REST API endpoints (subjects, learners, assessments, learning, etc.)
    services/           # Adaptive engine, subject loader, learner service, AI tutor
    data/
      subjects/         # Universal JSON subject definitions (Algebra, Python, Security, Physics)
  tests/                # Automated pytest suite
  requirements.txt      # Python dependencies
  .env.example          # Environment variable template
  README.md             # Backend documentation
```

## Setup & Running

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment (Optional)
Copy `.env.example` to `.env` and add your Gemini API key if available:
```bash
GEMINI_API_KEY=your_key_here
```

### 3. Start the FastAPI server
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at http://localhost:8000/docs.

### 4. Run automated tests
```bash
pytest tests/ -v
```
