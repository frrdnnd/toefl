from fastapi import APIRouter
from fastapi import Depends

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.history import PracticeHistory

from app.services.llm_service import ask_llm
from app.services.rag_service import get_context

import json

router = APIRouter()


# =========================
# DATABASE
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================
# REQUEST MODELS
# =========================

class QuestionRequest(BaseModel):
    category: str
    difficulty: str


class EvaluationRequest(BaseModel):
    question: str
    options: list[str]
    user_answer: str
    correct_answer: str
    category: str = "Grammar"
    difficulty: str = "Intermediate"


# =========================
# GENERATE QUESTION
# =========================

@router.post("/generate-question")
def generate_question(
    payload: QuestionRequest
):

    context = get_context(payload.category)

    prompt = f"""
You are a professional TOEFL tutor AI.

Use the TOEFL material below as reference.

TOEFL MATERIAL:
{context}

TASK:
Generate 1 TOEFL {payload.category} question.

Difficulty:
{payload.difficulty}

RULES:
- Generate high-quality TOEFL style question
- Provide 4 options
- Only one correct answer
- Add short explanation
- Keep grammar accurate
- Make it suitable for TOEFL learners

IMPORTANT:
Return ONLY valid JSON.
Do NOT include markdown.
Do NOT include explanation outside JSON.

FORMAT:

{{
  "question": "...",
  "options": [
    "A. ...",
    "B. ...",
    "C. ...",
    "D. ..."
  ],
  "answer": "A",
  "explanation": "..."
}}
"""

    response = ask_llm(
        question=prompt,
        options="",
        user_answer="",
        correct_answer=""
    )

    try:

        # jika response dict AI tutor
        if isinstance(response, dict):
            raise Exception("Use fallback parser")

        cleaned = response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()

        parsed = json.loads(cleaned)

        parsed["difficulty"] = payload.difficulty
        parsed["category"] = payload.category

        return parsed

    except Exception as e:

        print("QUESTION GENERATION ERROR:", e)

        return {
            "question": "Choose the correct sentence.",
            "options": [
                "A. She go to school.",
                "B. She goes to school.",
                "C. She going to school.",
                "D. She gone to school."
            ],
            "answer": "B",
            "difficulty": payload.difficulty,
            "category": payload.category,
            "explanation": (
                "Singular subject uses verb with s/es."
            )
        }


# =========================
# EVALUATE ANSWER
# =========================

@router.post("/evaluate-answer")
def evaluate_answer(
    payload: EvaluationRequest,
    db: Session = Depends(get_db)
):

    # =========================
    # ASK AI TUTOR
    # =========================
    # =========================
# GET FULL CORRECT OPTION
# =========================

    correct_option = next(
    (
        opt for opt in payload.options
        if opt.startswith(payload.correct_answer)
    ),
    payload.correct_answer
)
    parsed = ask_llm(
    question=payload.question,

    options=payload.options,

    user_answer=payload.user_answer,

correct_answer=correct_option)

    # =========================
    # AUTO DETECT CORRECTNESS
    # =========================

    is_correct = (
        payload.user_answer.strip().upper() ==
        payload.correct_answer.strip().upper()
    )

    # =========================
    # FALLBACK SAFETY
    # =========================

    if not isinstance(parsed, dict):

        parsed = {
            "correct_answer": payload.correct_answer,
            "translation": "Translation unavailable.",
            "explanation": "AI explanation unavailable.",
            "why_wrong": "Could not analyze answer.",
            "grammar_tip": "Review grammar fundamentals.",
            "toefl_tip": "Practice more TOEFL questions."
        }

    # =========================
    # SAVE DATABASE
    # =========================

    history = PracticeHistory(
        category=payload.category,
        difficulty=payload.difficulty,
        question=payload.question,
        user_answer=payload.user_answer,
        correct_answer=correct_option,
        is_correct=is_correct,
        analysis=parsed["explanation"],
        grammar_tip=parsed["grammar_tip"],
        improvement=parsed["toefl_tip"],
        weakness_detected=payload.category
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    # =========================
    # RETURN RESPONSE
    # =========================

    return {
        "is_correct": is_correct,
        "correct_answer": parsed["correct_answer"],
        "translation": parsed["translation"],
        "explanation": parsed["explanation"],
        "why_wrong": parsed["why_wrong"],
        "grammar_tip": parsed["grammar_tip"],
        "toefl_tip": parsed["toefl_tip"]
    }