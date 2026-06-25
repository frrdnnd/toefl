from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.config import normalize_category
from app.core.config import normalize_difficulty
from app.core.database import SessionLocal
from app.models.history import PracticeHistory
from app.services import llm_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _accuracy(correct: int, total: int) -> int:
    if total == 0:
        return 0
    return round((correct / total) * 100)


def estimate_toefl(accuracy: int):
    """Map an overall accuracy percentage to an estimated TOEFL ITP score.

    Based on the score bands:
      0-39%  -> below 400      71-85%  -> 520-580
      40-55% -> 400-450        86-100% -> 580-650
      56-70% -> 450-520
    """
    a = max(0, min(100, accuracy))

    if a < 40:
        score = round(310 + (a / 40) * 90)
        label = "Below 400"
    elif a < 56:
        score = round(400 + ((a - 40) / 16) * 50)
        label = "400-450"
    elif a < 71:
        score = round(450 + ((a - 56) / 15) * 70)
        label = "450-520"
    elif a < 86:
        score = round(520 + ((a - 71) / 15) * 60)
        label = "520-580"
    else:
        score = round(580 + ((a - 86) / 14) * 70)
        label = "580-650"

    if score < 450:
        level = "Beginner"
    elif score < 550:
        level = "Intermediate"
    else:
        level = "Advanced"

    return score, label, level


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    rows = db.query(PracticeHistory).all()

    total_questions = len(rows)
    correct_answers = sum(1 for row in rows if row.is_correct)
    wrong_answers = total_questions - correct_answers
    accuracy = _accuracy(correct_answers, total_questions)

    # Per-category accuracy (always show the three core sections).
    category_buckets = {
        "grammar": {"total": 0, "correct": 0},
        "vocabulary": {"total": 0, "correct": 0},
        "reading": {"total": 0, "correct": 0},
    }

    # Per-difficulty accuracy.
    difficulty_buckets = {
        "easy": {"total": 0, "correct": 0},
        "intermediate": {"total": 0, "correct": 0},
        "advanced": {"total": 0, "correct": 0},
    }

    for row in rows:
        cat = normalize_category(row.category)
        diff = normalize_difficulty(row.difficulty)

        if cat in category_buckets:
            category_buckets[cat]["total"] += 1
            category_buckets[cat]["correct"] += 1 if row.is_correct else 0

        if diff in difficulty_buckets:
            difficulty_buckets[diff]["total"] += 1
            difficulty_buckets[diff]["correct"] += 1 if row.is_correct else 0

    category_accuracy = {
        name: _accuracy(bucket["correct"], bucket["total"])
        for name, bucket in category_buckets.items()
    }
    difficulty_accuracy = {
        name: _accuracy(bucket["correct"], bucket["total"])
        for name, bucket in difficulty_buckets.items()
    }

    # Richer stats that also expose attempt counts so the UI can tell
    # "0% because all wrong" apart from "no attempts yet".
    def _stats(buckets):
        return {
            name: {
                "accuracy": _accuracy(bucket["correct"], bucket["total"]),
                "total": bucket["total"],
                "correct": bucket["correct"],
                "wrong": bucket["total"] - bucket["correct"],
            }
            for name, bucket in buckets.items()
        }

    category_stats = _stats(category_buckets)
    difficulty_stats = _stats(difficulty_buckets)

    # Weakness topics (reuse the deterministic AI-tutor analysis).
    weakness = llm_service.analyze_weakness(rows)

    score, label, level = estimate_toefl(accuracy)

    suggested_difficulty = (
        "Advanced" if accuracy >= 80
        else "Intermediate" if accuracy >= 60
        else "Easy"
    )

    return {
        # --- legacy keys (kept so existing UI keeps working) ---
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "accuracy": accuracy,
        "suggested_difficulty": suggested_difficulty,
        # --- new breakdowns ---
        "category_accuracy": category_accuracy,
        "difficulty_accuracy": difficulty_accuracy,
        "category_stats": category_stats,
        "difficulty_stats": difficulty_stats,
        "weakness_topics": weakness["weak_topics"],
        "estimated_toefl_score": score,
        "estimated_toefl_range": label,
        "learning_level": level,
    }
