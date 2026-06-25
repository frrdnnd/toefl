from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./smarttoefl.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def run_lightweight_migrations():
    """Add newly introduced columns to existing SQLite tables.

    SQLAlchemy's create_all() does not ALTER existing tables, so when new
    columns are added to a model we patch them in here. This keeps older
    smarttoefl.db files working without forcing the user to delete their data.
    """
    inspector = inspect(engine)

    if "practice_history" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("practice_history")
    }

    new_columns = {
        "estimated_toefl_range": "VARCHAR",
        "topic": "VARCHAR",
    }

    with engine.begin() as connection:
        for name, column_type in new_columns.items():
            if name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE practice_history ADD COLUMN {name} {column_type}"
                    )
                )