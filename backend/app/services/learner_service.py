import json
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.learner import Learner
from app.models.concept_mastery import ConceptMastery
from app.models.attempt import Attempt
from app.schemas.learner import ConceptRecordState, LearnerResponse
from app.services.adaptive_engine import adaptive_engine
from app.services.subject_service import subject_service

class LearnerService:
    @staticmethod
    def ensure_seed_learners(db: Session) -> None:
        """
        Seeds default demonstration learners if the database is empty.
        Alex Morgan (experienced demo profile) and Sam Rivera (struggling/beginner profile).
        """
        existing_count = db.query(Learner).count()
        if existing_count > 0:
            return

        # Seed Alex Morgan
        alex = Learner(name="Alex Morgan", active_subject_id="algebra", activity_log=json.dumps([]))
        db.add(alex)
        db.flush()

        alex_records = [
            ("algebra", "expressions", 88, 4, 3, 2),
            ("algebra", "linear", 34, 4, 3, 1),
            ("algebra", "graphs", 0, 0, 0, 1),
            ("python", "variables", 75, 3, 3, 2),
            ("python", "conditionals", 30, 2, 1, 1),
            ("python", "loops", 0, 0, 0, 1)
        ]
        for subj, concept, mastery, attempts, correct, diff in alex_records:
            now = datetime.utcnow().isoformat()
            db.add(ConceptMastery(
                learner_id=alex.id,
                subject_id=subj,
                concept_id=concept,
                mastery_score=mastery,
                attempts=attempts,
                correct_attempts=correct,
                accuracy=(correct / attempts) if attempts > 0 else 0.0,
                difficulty=diff,
                last_practiced=datetime.utcnow() if attempts > 0 else None,
                due_at=adaptive_engine.calculate_revision_date(True, mastery) if attempts > 0 else None,
                history_json=json.dumps([now] if attempts > 0 else [])
            ))

        # Seed Sam Rivera
        sam = Learner(name="Sam Rivera", active_subject_id="algebra", activity_log=json.dumps([]))
        db.add(sam)
        db.flush()

        sam_records = [
            ("algebra", "expressions", 28, 3, 1, 1),
            ("algebra", "linear", 0, 0, 0, 1),
            ("algebra", "graphs", 0, 0, 0, 1),
            ("python", "variables", 40, 2, 1, 1),
            ("python", "conditionals", 0, 0, 0, 1),
            ("python", "loops", 0, 0, 0, 1)
        ]
        for subj, concept, mastery, attempts, correct, diff in sam_records:
            now = datetime.utcnow().isoformat()
            db.add(ConceptMastery(
                learner_id=sam.id,
                subject_id=subj,
                concept_id=concept,
                mastery_score=mastery,
                attempts=attempts,
                correct_attempts=correct,
                accuracy=(correct / attempts) if attempts > 0 else 0.0,
                difficulty=diff,
                last_practiced=datetime.utcnow() if attempts > 0 else None,
                due_at=adaptive_engine.calculate_revision_date(False, mastery) if attempts > 0 else None,
                history_json=json.dumps([now] if attempts > 0 else [])
            ))

        db.commit()

    @staticmethod
    def get_all_learners(db: Session) -> List[Learner]:
        LearnerService.ensure_seed_learners(db)
        return db.query(Learner).all()

    @staticmethod
    def get_learner_by_id(db: Session, learner_id: int) -> Optional[Learner]:
        LearnerService.ensure_seed_learners(db)
        return db.query(Learner).filter(Learner.id == learner_id).first()

    @staticmethod
    def create_learner(db: Session, name: str) -> Learner:
        learner = Learner(name=name, active_subject_id="algebra", activity_log=json.dumps([]))
        db.add(learner)
        db.commit()
        db.refresh(learner)
        return learner

    @staticmethod
    def get_concept_records_for_learner(
        db: Session,
        learner_id: int,
        subject_id: Optional[str] = None
    ) -> Dict[str, ConceptRecordState]:
        query = db.query(ConceptMastery).filter(ConceptMastery.learner_id == learner_id)
        if subject_id:
            query = query.filter(ConceptMastery.subject_id == subject_id)
            
        records: Dict[str, ConceptRecordState] = {}
        for m in query.all():
            history = []
            if m.history_json:
                try:
                    history = json.loads(m.history_json)
                except Exception:
                    history = []
            records[m.concept_id] = ConceptRecordState(
                mastery=m.mastery_score,
                attempts=m.attempts,
                correct=m.correct_attempts,
                accuracy=m.accuracy,
                difficulty=m.difficulty,
                lastPracticed=m.last_practiced.isoformat() if m.last_practiced else None,
                dueAt=m.due_at.isoformat() if m.due_at else None,
                history=history
            )
        return records

    @staticmethod
    def get_learner_response(db: Session, learner: Learner) -> LearnerResponse:
        records = LearnerService.get_concept_records_for_learner(db, learner.id)
        activity = []
        if learner.activity_log:
            try:
                activity = json.loads(learner.activity_log)
            except Exception:
                activity = []
        return LearnerResponse(
            id=learner.id,
            name=learner.name,
            active_subject_id=learner.active_subject_id,
            records=records,
            activity=activity
        )

    @staticmethod
    def update_mastery_record(
        db: Session,
        learner_id: int,
        subject_id: str,
        concept_id: str,
        is_correct: bool,
        question_prompt: str,
        selected_answer: int,
        misconception: Optional[str] = None
    ) -> ConceptMastery:
        # Find or create mastery record
        mastery = (
            db.query(ConceptMastery)
            .filter(
                ConceptMastery.learner_id == learner_id,
                ConceptMastery.subject_id == subject_id,
                ConceptMastery.concept_id == concept_id
            )
            .first()
        )
        if not mastery:
            mastery = ConceptMastery(
                learner_id=learner_id,
                subject_id=subject_id,
                concept_id=concept_id,
                mastery_score=0,
                attempts=0,
                correct_attempts=0,
                accuracy=0.0,
                difficulty=1,
                consecutive_correct=0
            )
            db.add(mastery)
            db.flush()

        old_score = mastery.mastery_score
        new_score = adaptive_engine.calculate_mastery_update(
            old_mastery=old_score,
            is_correct=is_correct,
            current_attempts=mastery.attempts
        )
        new_due_at = adaptive_engine.calculate_revision_date(is_correct, new_score)
        new_diff, new_consec = adaptive_engine.adjust_difficulty(
            current_difficulty=mastery.difficulty,
            is_correct=is_correct,
            consecutive_correct=mastery.consecutive_correct
        )

        now = datetime.utcnow()
        history = []
        if mastery.history_json:
            try:
                history = json.loads(mastery.history_json)
            except Exception:
                history = []
        history.append(now.isoformat())

        mastery.mastery_score = new_score
        mastery.attempts += 1
        if is_correct:
            mastery.correct_attempts += 1
        mastery.accuracy = round(mastery.correct_attempts / mastery.attempts, 2)
        mastery.difficulty = new_diff
        mastery.consecutive_correct = new_consec
        mastery.last_practiced = now
        mastery.due_at = new_due_at
        mastery.history_json = json.dumps(history)

        # Record attempt
        attempt = Attempt(
            learner_id=learner_id,
            subject_id=subject_id,
            concept_id=concept_id,
            question_prompt=question_prompt,
            selected_answer=selected_answer,
            is_correct=is_correct,
            difficulty=mastery.difficulty,
            misconception_detected=misconception,
            timestamp=now
        )
        db.add(attempt)

        # Update activity log on learner
        learner = db.query(Learner).filter(Learner.id == learner_id).first()
        if learner:
            concept = subject_service.get_concept(subject_id, concept_id)
            title = concept.title if concept else concept_id
            verb = "Practised" if is_correct else "Reviewed"
            activity_entry = f"{verb} {title}"
            
            acts = []
            if learner.activity_log:
                try:
                    acts = json.loads(learner.activity_log)
                except Exception:
                    acts = []
            acts = [activity_entry] + acts
            learner.activity_log = json.dumps(acts[:6])

        db.commit()
        db.refresh(mastery)
        return mastery

learner_service = LearnerService()
