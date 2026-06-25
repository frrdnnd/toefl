from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

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


@router.get("/recommendation")
def get_recommendation(db: Session = Depends(get_db)):
    rows = db.query(PracticeHistory).all()

    total = len(rows)
    correct = sum(1 for row in rows if row.is_correct)
    accuracy = round((correct / total) * 100) if total else 0

    analysis = llm_service.analyze_weakness(rows)

    recommendations = analysis["recommendations"]
    weak_topics = analysis["weak_topics"]

    if total == 0:
        recommendation = (
            "Start practicing to unlock personalized AI recommendations."
        )
    else:
        recommendation = recommendations[0]

    suggested_difficulty = (
        "Advanced" if accuracy >= 80
        else "Intermediate" if accuracy >= 60
        else "Easy"
    )

    return {
        "recommendation": recommendation,
        "recommendations": recommendations,
        "weak_topics": weak_topics,
        "suggested_difficulty": suggested_difficulty,
    }
