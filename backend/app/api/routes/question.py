"""
Question generation and answer-checking endpoints.

New (preferred) API:
    GET  /api/questions/generate?category=&difficulty=&mode=
    POST /api/questions/check-answer

Legacy API (kept for backward compatibility with older clients):
    POST /generate-question
    POST /evaluate-answer
"""

import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import normalize_category
from app.core.config import normalize_difficulty
from app.core.config import estimated_range_for
from app.core.database import SessionLocal
from app.models.history import PracticeHistory
from app.services import llm_service
from app.services import question_bank


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class QuestionRequest(BaseModel):
    category: str
    difficulty: str
    mode: str = "dataset"


class CheckAnswerRequest(BaseModel):
    question_id: str = ""
    selected_answer: str
    correct_answer: str
    category: str = "grammar"
    difficulty: str = "intermediate"
    topic: str = ""
    # Optional context that lets us give richer feedback without a DB lookup.
    question: str = ""
    options: dict | list | None = None
    explanation: str = ""
    bilingual: bool = True


class EvaluationRequest(BaseModel):
    question: str
    options: list[str]
    user_answer: str
    correct_answer: str
    category: str = "Grammar"
    difficulty: str = "Intermediate"
    topic: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_id(data: dict, category: str, difficulty: str) -> dict:
    """Make sure a generated question carries a stable id for check-answer."""
    if not data.get("id"):
        data["id"] = f"{category}_{difficulty}_{uuid.uuid4().hex[:8]}"
    return data


def _resolve_correct_text(correct_letter: str, options) -> str:
    """Return a human-readable correct answer like 'A. did governments begin'."""
    letter = (correct_letter or "").strip().upper()[:1]

    if isinstance(options, dict):
        text = options.get(letter) or options.get(correct_letter)
        if text:
            return f"{letter}. {text}"

    if isinstance(options, list):
        for option in options:
            if str(option).strip().upper().startswith(letter):
                return str(option)

    return letter or str(correct_letter)


def _save_history(db, *, category, difficulty, topic, question, user_answer,
                  correct_answer, is_correct, feedback):
    history = PracticeHistory(
        category=category,
        difficulty=difficulty,
        estimated_toefl_range=estimated_range_for(difficulty),
        topic=topic,
        question=question,
        user_answer=user_answer,
        correct_answer=correct_answer,
        is_correct=is_correct,
        analysis=feedback.get("explanation", ""),
        grammar_tip=feedback.get("grammar_tip", ""),
        improvement=feedback.get("toefl_tip", ""),
        weakness_detected=(topic if not is_correct else ""),
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


# ---------------------------------------------------------------------------
# New API: generate
# ---------------------------------------------------------------------------

@router.get("/api/questions/generate")
def api_generate_question(
    category: str = Query("grammar"),
    difficulty: str = Query("intermediate"),
    mode: str = Query("dataset"),
):
    cat = normalize_category(category)
    diff = normalize_difficulty(difficulty)

    data, source = llm_service.generate_question(cat, diff, mode)
    data = _ensure_id(data, cat, diff)

    return {
        "success": True,
        "source": source,
        "rag_used": bool(data.get("rag_used", False)),
        "data": data,
    }


# ---------------------------------------------------------------------------
# New API: check-answer
# ---------------------------------------------------------------------------

@router.post("/api/questions/check-answer")
def api_check_answer(
    payload: CheckAnswerRequest,
    db: Session = Depends(get_db),
):
    cat = normalize_category(payload.category)
    diff = normalize_difficulty(payload.difficulty)

    selected = (payload.selected_answer or "").strip().upper()[:1]
    correct = (payload.correct_answer or "").strip().upper()[:1]
    is_correct = bool(selected) and selected == correct

    # Resolve options/explanation, falling back to the question bank if needed.
    options = payload.options
    explanation = payload.explanation
    question_text = payload.question
    topic = (payload.topic or "").strip()

    if (not options or not explanation or not topic) and payload.question_id:
        stored = question_bank.get_question_by_id(payload.question_id)
        if stored:
            options = options or stored.get("options")
            explanation = explanation or stored.get("explanation", "")
            question_text = question_text or stored.get("question", "")
            topic = topic or stored.get("topic") or stored.get("type", "")

    if not topic:
        topic = cat

    correct_text = _resolve_correct_text(correct, options)

    feedback = llm_service.generate_explanation(
        question=question_text,
        options=options,
        user_answer=selected,
        correct_answer=correct_text,
        is_correct=is_correct,
        base_explanation=explanation,
        use_llm=payload.bilingual,
        category=cat,
    )

    weakness_detected = "" if is_correct else topic
    recommendation = (
        "Great job! Keep practicing to maintain your progress."
        if is_correct
        else llm_service.recommend_for_topic(topic, cat)
    )

    _save_history(
        db,
        category=payload.category,
        difficulty=payload.difficulty,
        topic=topic,
        question=question_text,
        user_answer=selected,
        correct_answer=correct_text,
        is_correct=is_correct,
        feedback=feedback,
    )

    return {
        "is_correct": is_correct,
        "correct_answer": correct,
        "correct_answer_text": correct_text,
        "explanation": explanation or feedback.get("explanation", ""),
        "weakness_detected": weakness_detected,
        "recommendation": recommendation,
        "topic": topic,
        "rag_used": bool(feedback.get("rag_used", False)),
        # Bilingual extras (preserved from the original UI feature set).
        "translation": feedback.get("translation", ""),
        "explanation_id": feedback.get("explanation_id", ""),
        "why_wrong": feedback.get("why_wrong", "") if not is_correct else "",
        "why_wrong_id": feedback.get("why_wrong_id", "") if not is_correct else "",
        "grammar_tip": feedback.get("grammar_tip", ""),
        "grammar_tip_id": feedback.get("grammar_tip_id", ""),
        "toefl_tip": feedback.get("toefl_tip", ""),
        "toefl_tip_id": feedback.get("toefl_tip_id", ""),
    }


# ---------------------------------------------------------------------------
# Legacy API: /generate-question (list-style options)
# ---------------------------------------------------------------------------

@router.post("/generate-question")
def generate_question(payload: QuestionRequest):
    cat = normalize_category(payload.category)
    diff = normalize_difficulty(payload.difficulty)

    data, source = llm_service.generate_question(cat, diff, payload.mode)

    # Flatten to the legacy shape: options as an "A. ..." string list.
    if data.get("section") == "reading":
        first = (data.get("questions") or [{}])[0]
        question_text = f"{data.get('passage', '')}\n\n{first.get('question', '')}".strip()
        options_dict = first.get("options", {})
        answer = first.get("answer", "A")
        explanation = first.get("explanation", "")
    else:
        question_text = data.get("question", "")
        options_dict = data.get("options", {})
        answer = data.get("answer", "A")
        explanation = data.get("explanation", "")

    options_list = [
        f"{letter}. {options_dict.get(letter, '')}"
        for letter in ("A", "B", "C", "D")
        if options_dict.get(letter)
    ]

    return {
        "question": question_text,
        "options": options_list,
        "answer": answer,
        "explanation": explanation,
        "difficulty": payload.difficulty,
        "category": payload.category,
        "topic": data.get("topic", cat),
        "estimated_toefl_range": data.get("estimated_toefl_range", estimated_range_for(diff)),
        "source": source,
    }


# ---------------------------------------------------------------------------
# Legacy API: /evaluate-answer (bilingual feedback)
# ---------------------------------------------------------------------------

@router.post("/evaluate-answer")
def evaluate_answer(
    payload: EvaluationRequest,
    db: Session = Depends(get_db),
):
    correct_text = _resolve_correct_text(payload.correct_answer, payload.options)

    is_correct = (
        payload.user_answer.strip().upper()[:1]
        == payload.correct_answer.strip().upper()[:1]
    )

    feedback = llm_service.generate_explanation(
        question=payload.question,
        options=payload.options,
        user_answer=payload.user_answer,
        correct_answer=correct_text,
        is_correct=is_correct,
        use_llm=True,
        category=payload.category,
    )

    topic = (payload.topic or "").strip() or payload.category

    _save_history(
        db,
        category=payload.category,
        difficulty=payload.difficulty,
        topic=topic,
        question=payload.question,
        user_answer=payload.user_answer,
        correct_answer=correct_text,
        is_correct=is_correct,
        feedback=feedback,
    )

    return {
        "is_correct": is_correct,
        "correct_answer": correct_text,
        "translation": feedback.get("translation", ""),
        "explanation": feedback.get("explanation", ""),
        "explanation_id": feedback.get("explanation_id", ""),
        "why_wrong": feedback.get("why_wrong", "") if not is_correct else "",
        "why_wrong_id": feedback.get("why_wrong_id", "") if not is_correct else "",
        "grammar_tip": feedback.get("grammar_tip", ""),
        "grammar_tip_id": feedback.get("grammar_tip_id", ""),
        "toefl_tip": feedback.get("toefl_tip", ""),
        "toefl_tip_id": feedback.get("toefl_tip_id", ""),
        "recommendation": llm_service.recommend_for_topic(topic, payload.category),
        "rag_used": bool(feedback.get("rag_used", False)),
    }


# ---------------------------------------------------------------------------
# RAG status (for demos / debugging)
# ---------------------------------------------------------------------------

@router.get("/api/rag/status")
def rag_status():
    from app.core import config
    from app.services import rag_service

    return {
        "enabled": config.USE_RAG,
        "ready": rag_service.is_ready(),
        "top_k": config.RAG_TOP_K,
        "provider": config.LLM_PROVIDER,
    }
