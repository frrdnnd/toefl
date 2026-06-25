from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.config import normalize_category
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


@router.get("/weakness-analysis")
def weakness_analysis(db: Session = Depends(get_db)):
    rows = db.query(PracticeHistory).all()

    buckets = {
        "grammar": {"total": 0, "correct": 0},
        "vocabulary": {"total": 0, "correct": 0},
        "reading": {"total": 0, "correct": 0},
    }

    for row in rows:
        cat = normalize_category(row.category)
        if cat in buckets:
            buckets[cat]["total"] += 1
            buckets[cat]["correct"] += 1 if row.is_correct else 0

    def accuracy(bucket):
        if bucket["total"] == 0:
            return 0
        return round((bucket["correct"] / bucket["total"]) * 100)

    analysis = llm_service.analyze_weakness(rows)

    return {
        # Per-category accuracy (keys kept for the existing dashboard charts).
        "grammar": accuracy(buckets["grammar"]),
        "vocabulary": accuracy(buckets["vocabulary"]),
        "reading": accuracy(buckets["reading"]),
        # AI-tutor style detail.
        "weak_topics": analysis["weak_topics"],
        "recommendations": analysis["recommendations"],
    }
