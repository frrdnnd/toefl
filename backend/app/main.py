from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base
from app.core.database import engine

from app.models.history import PracticeHistory

from app.api.routes.question import router as question_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.history import router as history_router
from app.api.routes.recommendation import router as recommendation_router
from app.api.routes.weakness import router as weakness_router

# CREATE TABLES
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMARTTOEFL AI API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(question_router)
app.include_router(analytics_router)
app.include_router(history_router)
app.include_router(recommendation_router)
app.include_router(weakness_router)


@app.get("/")
def root():
    return {
        "message": "SMARTTOEFL AI Backend Running"
    }