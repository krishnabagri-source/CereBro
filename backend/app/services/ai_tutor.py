import json
import logging
from typing import Dict, Any, List, Optional
from app.config import settings
from app.schemas.subject import ConceptSchema, QuestionSchema

logger = logging.getLogger(__name__)

class AITutorService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._gemini_client = None

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._gemini_client = genai.GenerativeModel(self.model_name)
                logger.info("Gemini AI Tutor client configured successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}. Will use pedagogical fallback.")

    def explain_concept(
        self,
        subject_name: str,
        concept: ConceptSchema,
        learner_mastery: int,
        difficulty_level: int
    ) -> Dict[str, Any]:
        """
        Explains concept adapted to the student's current mastery and difficulty level.
        """
        prompt = (
            f"You are AdaptIQ, an empathetic and pedagogical AI Tutor for {subject_name}.\n"
            f"Explain the concept '{concept.title}' at academic level '{concept.level}'.\n"
            f"Student's current mastery is {learner_mastery}%, difficulty tier {difficulty_level}.\n"
            f"Concept description: {concept.description}\n"
            f"Key learning objectives: {', '.join(concept.learning_objectives or [])}\n"
            f"Lesson reference: {concept.lesson}\n"
            f"Provide an intuitive, clear explanation with a simple real-world analogy. Keep it concise (under 160 words)."
        )

        response_text = self._call_gemini(prompt)
        if response_text:
            return {
                "text": response_text.strip(),
                "is_ai_generated": True
            }

        # Deterministic Fallback
        mastery_tone = (
            "Let's build strong foundations together! "
            if learner_mastery < 50
            else "You're making steady progress! Let's refine your understanding: "
        )
        return {
            "text": f"{mastery_tone}{concept.lesson} For example: {concept.example}",
            "is_ai_generated": False
        }

    def provide_hint(
        self,
        subject_name: str,
        concept: ConceptSchema,
        question: QuestionSchema,
        attempt_number: int = 1
    ) -> Dict[str, Any]:
        """
        Provides progressive hints without giving away the direct answer choice.
        """
        # If question already has verified hints, prefer progressive hint from bank
        hints = question.hints or []
        if hints:
            hint_idx = min(attempt_number - 1, len(hints) - 1)
            hint_text = hints[hint_idx]
            return {
                "hint": hint_text,
                "is_ai_generated": False
            }

        prompt = (
            f"You are an AI Tutor in {subject_name}. The student is solving this question:\n"
            f"'{question.prompt}' for concept '{concept.title}'.\n"
            f"Give a single helpful pedagogical hint (attempt #{attempt_number}) without revealing the exact answer."
        )

        ai_hint = self._call_gemini(prompt)
        if ai_hint:
            return {
                "hint": ai_hint.strip(),
                "is_ai_generated": True
            }

        return {
            "hint": f"Recall the core rule for {concept.title}: {concept.lesson}",
            "is_ai_generated": False
        }

    def generate_practice_question(
        self,
        subject_name: str,
        concept: ConceptSchema,
        difficulty: int = 1
    ) -> Dict[str, Any]:
        """
        Generates or selects an adaptive question tailored to the learner's difficulty.
        """
        # First check verified question bank in concept
        if concept.question_bank:
            matching = [q for q in concept.question_bank if q.difficulty == difficulty]
            if matching:
                selected = matching[0]
                return {
                    "question": selected.model_dump(),
                    "is_ai_generated": False
                }

        prompt = (
            f"Generate a multiple-choice practice question for {subject_name}, concept '{concept.title}'.\n"
            f"Difficulty tier: {difficulty}/3.\n"
            f"Output strictly valid JSON with keys: prompt (str), choices (list of 3 or 4 strings), "
            f"answer (int 0-indexed correct choice), explanation (str), hints (list of 1-2 str strings).\n"
            f"Do not include markdown or code fences."
        )

        response_text = self._call_gemini(prompt)
        if response_text:
            try:
                # Strip backticks if any
                clean_text = response_text.strip().replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)
                if "prompt" in data and "choices" in data and "answer" in data:
                    data["difficulty"] = difficulty
                    return {
                        "question": data,
                        "is_ai_generated": True
                    }
            except Exception as e:
                logger.warning(f"Failed to parse AI generated question JSON: {e}")

        # Fallback to standard verified practice
        return {
            "question": concept.practice.model_dump(),
            "is_ai_generated": False
        }

    def analyze_incorrect_answer(
        self,
        subject_name: str,
        concept: ConceptSchema,
        question: QuestionSchema,
        chosen_index: int,
        student_reasoning: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes student's incorrect response, detects underlying misconception, and explains clearly.
        """
        chosen_text = question.choices[chosen_index] if 0 <= chosen_index < len(question.choices) else "unknown"
        correct_text = question.choices[question.answer] if 0 <= question.answer < len(question.choices) else "unknown"

        prompt = (
            f"You are an AI Tutor diagnosing a student error in {subject_name} on '{concept.title}'.\n"
            f"Question: '{question.prompt}'\n"
            f"Student picked: '{chosen_text}'\n"
            f"Correct answer: '{correct_text}'\n"
            f"Student reasoning: '{student_reasoning or 'None provided'}'\n"
            f"Identify the likely misconception and provide a friendly, constructive 2-3 sentence correction."
        )

        ai_feedback = self._call_gemini(prompt)
        if ai_feedback:
            return {
                "feedback": ai_feedback.strip(),
                "is_ai_generated": True
            }

        # Deterministic fallback
        return {
            "feedback": (
                f"Notice that '{chosen_text}' does not match the rule: {question.explanation} "
                f"Reviewing '{concept.title}' will help avoid this mistake!"
            ),
            "is_ai_generated": False
        }

    def answer_student_doubt(
        self,
        subject_name: str,
        concept: ConceptSchema,
        query: str,
        learner_mastery: int
    ) -> Dict[str, Any]:
        """
        Answers open student questions regarding the subject concept.
        """
        prompt = (
            f"You are AdaptIQ, a friendly personal tutor for {subject_name}.\n"
            f"The student (mastery: {learner_mastery}%) is asking about '{concept.title}':\n"
            f"\"{query}\"\n"
            f"Reference concept material: {concept.lesson}\n"
            f"Give a clear, accurate, and encouraging answer in under 150 words."
        )

        response_text = self._call_gemini(prompt)
        if response_text:
            return {
                "answer": response_text.strip(),
                "is_ai_generated": True
            }

        return {
            "answer": (
                f"Great question! In {concept.title}: {concept.lesson} "
                f"Keep exploring: {concept.example}"
            ),
            "is_ai_generated": False
        }

    def _call_gemini(self, prompt: str) -> Optional[str]:
        if not self._gemini_client:
            return None
        try:
            response = self._gemini_client.generate_content(prompt)
            if response and hasattr(response, "text"):
                return response.text
        except Exception as e:
            logger.warning(f"Gemini API request failed: {e}")
        return None

ai_tutor = AITutorService()
