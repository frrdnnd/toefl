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


@router.get("/recommendation")
def get_recommendation(db: Session = Depends(get_db)):

    grammar_wrong = db.query(PracticeHistory)\
        .filter(
            PracticeHistory.category == "Grammar",
            PracticeHistory.is_correct == False
        )\
        .count()

    if grammar_wrong > 5:
        recommendation = (
            "Practice more Subject Verb Agreement questions."
        )
    else:
        recommendation = (
            "Your TOEFL performance is improving consistently."
        )

    return {
        "recommendation": recommendation
    }