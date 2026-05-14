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


@router.get("/weakness-analysis")
def weakness_analysis(db: Session = Depends(get_db)):

    grammar_total = db.query(PracticeHistory)\
        .filter(PracticeHistory.category == "Grammar")\
        .count()

    grammar_wrong = db.query(PracticeHistory)\
        .filter(
            PracticeHistory.category == "Grammar",
            PracticeHistory.is_correct == False
        )\
        .count()

    def calculate(total, wrong):
        if total == 0:
            return 100

        return round(((total - wrong) / total) * 100)

    return {
        "grammar": calculate(grammar_total, grammar_wrong),
        "vocabulary": 80,
        "reading": 75
    }