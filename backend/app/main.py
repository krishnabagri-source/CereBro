from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.services.learner_service import learner_service
from app.services.subject_service import subject_service
from app.routers import (
    subjects,
    learners,
    assessments,
    learning,
    recommendations,
    revisions,
    state
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed default learners
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        learner_service.ensure_seed_learners(db)
        subject_service.load_all_subjects()
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Subject-independent, modular adaptive backend with AI tutor services.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api
app.include_router(subjects.router, prefix="/api")
app.include_router(learners.router, prefix="/api")
app.include_router(assessments.router, prefix="/api")
app.include_router(learning.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(revisions.router, prefix="/api")
app.include_router(state.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Welcome to AdaptIQ Universal Adaptive Backend",
        "docs": "/docs",
        "api": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
