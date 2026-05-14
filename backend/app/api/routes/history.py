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


@router.get("/history")
def get_history(
    db: Session = Depends(get_db)
):

    history = db.query(
        PracticeHistory
    ).order_by(
        PracticeHistory.created_at.desc()
    ).all()

    return history


@router.delete("/history")
def clear_history(
    db: Session = Depends(get_db)
):

    db.query(
        PracticeHistory
    ).delete()

    db.commit()

    return {
        "message": "History cleared successfully"
    }