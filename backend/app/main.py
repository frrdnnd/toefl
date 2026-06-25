from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base
from app.core.database import engine
from app.core.database import run_lightweight_migrations

from app.models.history import PracticeHistory

from app.api.routes.question import router as question_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.history import router as history_router
from app.api.routes.recommendation import router as recommendation_router
from app.api.routes.weakness import router as weakness_router

# CREATE TABLES
Base.metadata.create_all(bind=engine)

# Patch in any newly added columns for existing databases.
run_lightweight_migrations()

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


# Warm up the RAG model in the background so the first real request is fast.
# This never blocks startup and never crashes the app if RAG is unavailable.
@app.on_event("startup")
def _warm_up_rag():
    from app.core import config

    if not config.USE_RAG:
        return

    import threading

    def _job():
        try:
            from app.services.rag_service import warm_up

            ready = warm_up()
            print(f"RAG warm-up complete (ready={ready})")
        except Exception as error:
            print("RAG warm-up failed:", error)

    threading.Thread(target=_job, daemon=True).start()