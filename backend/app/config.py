import os
from pathlib import Path
from dotenv import load_dotenv

# Locate base directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "AdaptIQ — Universal Adaptive AI Tutor"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # SQLite Database
    DATABASE_PATH: Path = BASE_DIR / "data" / "adaptiq.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")
    
    # Subject definitions directory
    SUBJECTS_DIR: Path = Path(__file__).resolve().parent / "data" / "subjects"
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

settings = Settings()
