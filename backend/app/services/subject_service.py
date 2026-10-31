import json
from pathlib import Path
from typing import Dict, List, Optional
from app.config import settings
from app.schemas.subject import SubjectDetail, SubjectSummary, ConceptSchema, DiagnosticQuestionSchema

class SubjectService:
    def __init__(self, subjects_dir: Optional[Path] = None):
        self.subjects_dir = subjects_dir or settings.SUBJECTS_DIR
        self._subjects: Dict[str, SubjectDetail] = {}
        self.load_all_subjects()

    def load_all_subjects(self) -> None:
        self._subjects.clear()
        if not self.subjects_dir.exists():
            return
            
        for file_path in self.subjects_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    subject = SubjectDetail(**data)
                    self._subjects[subject.id] = subject
            except Exception as e:
                print(f"Error loading subject from {file_path}: {e}")

    def list_subjects(self) -> List[SubjectSummary]:
        return [
            SubjectSummary(
                id=s.id,
                name=s.name,
                domain=s.domain,
                level=s.level,
                description=s.description,
                icon=s.icon,
                color=s.color,
                concepts_count=len(s.concepts)
            )
            for s in self._subjects.values()
        ]

    def get_subject(self, subject_id: str) -> Optional[SubjectDetail]:
        if subject_id not in self._subjects:
            self.load_all_subjects()  # reload in case new file added
        return self._subjects.get(subject_id)

    def get_concept(self, subject_id: str, concept_id: str) -> Optional[ConceptSchema]:
        subject = self.get_subject(subject_id)
        if not subject:
            return None
        for concept in subject.concepts:
            if concept.id == concept_id:
                return concept
        return None

subject_service = SubjectService()
