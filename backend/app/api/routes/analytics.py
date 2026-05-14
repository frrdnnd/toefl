from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.history import PracticeHistory

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):

    total_questions = db.query(PracticeHistory).count()

    correct_answers = db.query(PracticeHistory)\
        .filter(PracticeHistory.is_correct == True)\
        .count()

    wrong_answers = db.query(PracticeHistory)\
        .filter(PracticeHistory.is_correct == False)\
        .count()

    accuracy = 0

    if total_questions > 0:
        accuracy = round(
            (correct_answers / total_questions) * 100
        )

    suggested_difficulty = (
        "Advanced"
        if accuracy >= 80
        else "Intermediate"
        if accuracy >= 60
        else "Easy"
    )

    return {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "accuracy": accuracy,
        "suggested_difficulty": suggested_difficulty
    }