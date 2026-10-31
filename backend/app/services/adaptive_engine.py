from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.schemas.subject import SubjectDetail, ConceptSchema
from app.schemas.learner import ConceptRecordState
from app.schemas.recommendation import RecommendationResponse, RoadmapItemResponse, RevisionItemResponse

class AdaptiveEngine:
    MASTERY_PREREQUISITE_THRESHOLD = 60
    MASTERY_COMPLETED_THRESHOLD = 80
    MAX_STEP_CHANGE = 18

    @staticmethod
    def calculate_mastery_update(
        old_mastery: int,
        is_correct: bool,
        current_attempts: int
    ) -> int:
        """
        Explainable mastery algorithm:
        - If 0 attempts: 50% if correct, 10% if incorrect.
        - Subsequent attempts: Exponential Moving Average (70% previous, 30% new evidence).
        - Single attempt change is clamped to MAX_STEP_CHANGE (+/- 18 points).
        - Clamped strictly between 0 and 100.
        """
        if current_attempts == 0:
            return 50 if is_correct else 10
            
        target_score = 100 if is_correct else 0
        ema = (old_mastery * 0.70) + (target_score * 0.30)
        raw_change = round(ema - old_mastery)
        capped_change = max(-AdaptiveEngine.MAX_STEP_CHANGE, min(AdaptiveEngine.MAX_STEP_CHANGE, raw_change))
        new_mastery = max(0, min(100, old_mastery + capped_change))
        return new_mastery

    @staticmethod
    def calculate_revision_date(is_correct: bool, new_mastery: int) -> datetime:
        """
        Spaced repetition scheduling:
        - Incorrect answer: Review tomorrow (+1 day).
        - Correct with mastery < 70%: Review in 2 days (+2 days).
        - Correct with mastery 70-84%: Review in 4 days (+4 days).
        - Correct with mastery >= 85%: Review in 7 days (+7 days).
        """
        now = datetime.utcnow()
        if not is_correct:
            return now + timedelta(days=1)
        elif new_mastery < 70:
            return now + timedelta(days=2)
        elif new_mastery < 85:
            return now + timedelta(days=4)
        else:
            return now + timedelta(days=7)

    @staticmethod
    def adjust_difficulty(
        current_difficulty: int,
        is_correct: bool,
        consecutive_correct: int
    ) -> Tuple[int, int]:
        """
        Adjust question difficulty:
        - Two consecutive correct answers bump difficulty up (max 3).
        - Any incorrect answer resets consecutive count and drops difficulty (min 1).
        """
        if is_correct:
            new_consecutive = consecutive_correct + 1
            new_difficulty = current_difficulty
            if new_consecutive >= 2 and current_difficulty < 3:
                new_difficulty += 1
                new_consecutive = 0
            return new_difficulty, new_consecutive
        else:
            new_difficulty = max(1, current_difficulty - 1)
            return new_difficulty, 0

    @staticmethod
    def check_prerequisites(
        concept: ConceptSchema,
        records: Dict[str, ConceptRecordState]
    ) -> Tuple[bool, List[str]]:
        """
        A concept is ready if each of its prerequisites has reached at least 60% mastery.
        """
        missing = []
        for prereq_id in concept.prerequisites:
            prereq_record = records.get(prereq_id)
            mastery = prereq_record.mastery if prereq_record else 0
            if mastery < AdaptiveEngine.MASTERY_PREREQUISITE_THRESHOLD:
                missing.append(prereq_id)
        return len(missing) == 0, missing

    @staticmethod
    def generate_roadmap(
        subject: SubjectDetail,
        records: Dict[str, ConceptRecordState]
    ) -> List[RoadmapItemResponse]:
        roadmap_items = []
        for concept in subject.concepts:
            record = records.get(concept.id, ConceptRecordState())
            prereqs_met, missing = AdaptiveEngine.check_prerequisites(concept, records)
            
            if record.mastery >= AdaptiveEngine.MASTERY_COMPLETED_THRESHOLD:
                status = "completed"
            elif record.attempts > 0:
                status = "in-progress"
            elif prereqs_met:
                status = "ready"
            else:
                status = "locked"

            roadmap_items.append(
                RoadmapItemResponse(
                    concept=concept,
                    record=record,
                    status=status,
                    prerequisites_met=prereqs_met,
                    missing_prerequisites=missing
                )
            )
        return roadmap_items

    @staticmethod
    def get_recommendation(
        subject: SubjectDetail,
        records: Dict[str, ConceptRecordState],
        learner_id: int
    ) -> RecommendationResponse:
        """
        Personalized, prerequisite-aware recommendation logic:
        1. Weak concepts in progress (attempts > 0, mastery < 60%) among unlocked concepts.
        2. Unstarted ready concepts whose prerequisites are fulfilled.
        3. Lowest mastery among ready concepts.
        4. If all concepts are mastered, recommend the concept with the earliest lastPracticed date for retention.
        """
        weak_concepts = []
        mastered_concepts = []

        unlocked_concepts = []
        for concept in subject.concepts:
            record = records.get(concept.id, ConceptRecordState())
            prereqs_met, _ = AdaptiveEngine.check_prerequisites(concept, records)
            
            if record.mastery >= AdaptiveEngine.MASTERY_COMPLETED_THRESHOLD:
                mastered_concepts.append(concept.id)
            elif record.attempts > 0 and record.mastery < AdaptiveEngine.MASTERY_PREREQUISITE_THRESHOLD:
                weak_concepts.append(concept.id)

            if prereqs_met:
                unlocked_concepts.append((concept, record))

        if not unlocked_concepts:
            # Fallback to first concept
            first_concept = subject.concepts[0] if subject.concepts else None
            return RecommendationResponse(
                learner_id=learner_id,
                subject_id=subject.id,
                recommended_concept=first_concept,
                reason="Begin your learning journey with this foundational concept.",
                priority_level="normal",
                weak_concepts=weak_concepts,
                mastered_concepts=mastered_concepts
            )

        # Priority 1: In-progress weak concepts (< 60% mastery)
        in_progress_weak = [
            (c, r) for c, r in unlocked_concepts
            if r.attempts > 0 and r.mastery < AdaptiveEngine.MASTERY_PREREQUISITE_THRESHOLD
        ]
        if in_progress_weak:
            # Sort by lowest mastery first
            in_progress_weak.sort(key=lambda item: item[1].mastery)
            chosen_concept, chosen_record = in_progress_weak[0]
            return RecommendationResponse(
                learner_id=learner_id,
                subject_id=subject.id,
                recommended_concept=chosen_concept,
                reason=f"Recommended because your current mastery is {chosen_record.mastery}%. Reinforcing this concept will solidify your foundation.",
                priority_level="high",
                weak_concepts=weak_concepts,
                mastered_concepts=mastered_concepts
            )

        # Priority 2: Unstarted ready concepts
        unstarted = [
            (c, r) for c, r in unlocked_concepts if r.attempts == 0
        ]
        if unstarted:
            chosen_concept, _ = unstarted[0]
            return RecommendationResponse(
                learner_id=learner_id,
                subject_id=subject.id,
                recommended_concept=chosen_concept,
                reason="You've mastered all prerequisites! This is the natural next step in your learning path.",
                priority_level="normal",
                weak_concepts=weak_concepts,
                mastered_concepts=mastered_concepts
            )

        # Priority 3: Ready concepts not yet mastered (< 80%)
        not_mastered = [
            (c, r) for c, r in unlocked_concepts if r.mastery < AdaptiveEngine.MASTERY_COMPLETED_THRESHOLD
        ]
        if not_mastered:
            not_mastered.sort(key=lambda item: item[1].mastery)
            chosen_concept, chosen_record = not_mastered[0]
            return RecommendationResponse(
                learner_id=learner_id,
                subject_id=subject.id,
                recommended_concept=chosen_concept,
                reason=f"Continue practicing to bring your mastery from {chosen_record.mastery}% to 80%+ mastery.",
                priority_level="normal",
                weak_concepts=weak_concepts,
                mastered_concepts=mastered_concepts
            )

        # Priority 4: All mastered -> Recommend retention review
        unlocked_concepts.sort(key=lambda item: item[1].lastPracticed or "")
        chosen_concept, chosen_record = unlocked_concepts[0]
        return RecommendationResponse(
            learner_id=learner_id,
            subject_id=subject.id,
            recommended_concept=chosen_concept,
            reason="Outstanding progress! A quick review session will ensure long-term retention.",
            priority_level="review",
            weak_concepts=weak_concepts,
            mastered_concepts=mastered_concepts
        )

    @staticmethod
    def detect_misconception(
        concept: ConceptSchema,
        selected_index: int,
        student_reasoning: Optional[str] = None
    ) -> Optional[str]:
        """
        Detects if a chosen incorrect option or reasoning corresponds to a known misconception.
        """
        if selected_index == concept.practice.answer:
            return None

        # Check common misconceptions configured for this concept
        if concept.common_misconceptions:
            # If student reasoning was given, check for keyword overlap
            if student_reasoning:
                lower_reason = student_reasoning.lower()
                for item in concept.common_misconceptions:
                    keywords = [w for w in item.misconception.lower().split() if len(w) > 3]
                    if any(k in lower_reason for k in keywords):
                        return f"{item.misconception}: {item.explanation}"
            
            # Default to the most relevant concept misconception
            first = concept.common_misconceptions[0]
            return f"{first.misconception}: {first.explanation}"

        return None

adaptive_engine = AdaptiveEngine()
