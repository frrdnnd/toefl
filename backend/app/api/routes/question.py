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

    # =========================
    # GET RAG CONTEXT
    # =========================

    context = get_context(payload.category)

    # =========================
    # AI PROMPT
    # =========================

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

    # =========================
    # ASK LLM
    # =========================

    response = ask_llm(prompt)

    try:

        cleaned = response.strip()

        # Remove markdown block
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
        print("RAW RESPONSE:", response)

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
    # GET RAG CONTEXT
    # =========================

    context = get_context(payload.category)

    # =========================
    # AI PROMPT
    # =========================

    prompt = f"""
You are an adaptive TOEFL evaluator AI.

Use the TOEFL material below.

TOEFL MATERIAL:
{context}

QUESTION:
{payload.question}

CORRECT ANSWER:
{payload.correct_answer}

USER ANSWER:
{payload.user_answer}

TASK:
Analyze the user's TOEFL answer.

RULES:
- Determine if answer is correct
- Explain grammar issue
- Detect weakness
- Give improvement suggestion
- Keep response educational
- Keep response concise

IMPORTANT:
Return ONLY valid JSON.
Do NOT include markdown.
Do NOT include extra explanation.

FORMAT:

{{
  "is_correct": true,
  "analysis": "...",
  "grammar_tip": "...",
  "improvement": "...",
  "weakness_detected": "..."
}}
"""

    # =========================
    # ASK LLM
    # =========================

    response = ask_llm(prompt)

    try:

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

    except Exception as e:

        print("EVALUATION ERROR:", e)
        print("RAW RESPONSE:", response)

        # fallback
        parsed = {
            "is_correct": (
                payload.user_answer ==
                payload.correct_answer
            ),
            "analysis": (
                "AI evaluation failed. "
                "Using fallback evaluation."
            ),
            "grammar_tip": (
                "Review grammar fundamentals."
            ),
            "improvement": (
                "Practice more TOEFL questions."
            ),
            "weakness_detected": (
                payload.category
            )
        }

    # =========================
    # SAVE DATABASE
    # =========================

    history = PracticeHistory(
        category=payload.category,
        difficulty=payload.difficulty,
        question=payload.question,
        user_answer=payload.user_answer,
        correct_answer=payload.correct_answer,
        is_correct=parsed["is_correct"],
        analysis=parsed["analysis"],
        grammar_tip=parsed["grammar_tip"],
        improvement=parsed["improvement"],
        weakness_detected=parsed["weakness_detected"]
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    # =========================
    # RETURN RESPONSE
    # =========================

    return parsed