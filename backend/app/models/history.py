from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class PracticeHistory(Base):

    __tablename__ = "practice_history"

    id = Column(Integer, primary_key=True, index=True)

    category = Column(String)
    difficulty = Column(String)

    question = Column(String)

    user_answer = Column(String)
    correct_answer = Column(String)

    is_correct = Column(Boolean)

    analysis = Column(String)
    grammar_tip = Column(String)
    improvement = Column(String)

    weakness_detected = Column(String)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )