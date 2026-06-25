"""
Local question bank service.

Loads TOEFL questions from JSON files in `app/dataset/questions/` and serves
them by category and difficulty. This is the deterministic fallback used when
no LLM is available (or when the user picks the "dataset" mode), so the app
never crashes just because Ollama/OpenAI is offline.
"""

import json
import random
from pathlib import Path

from app.core.config import normalize_category
from app.core.config import normalize_difficulty
from app.core.config import estimated_range_for

# .../app/services/question_bank.py -> .../app/dataset/questions
QUESTIONS_DIR = Path(__file__).resolve().parent.parent / "dataset" / "questions"

# Simple in-memory cache so we do not re-read JSON files on every request.
_CACHE: dict[str, list] = {}


def _file_key(category: str, difficulty: str) -> str:
    cat = normalize_category(category)
    diff = normalize_difficulty(difficulty)
    return f"{cat}_{diff}"


def load_questions(category: str, difficulty: str) -> list:
    """Return the full list of questions for a category/difficulty (cached)."""
    key = _file_key(category, difficulty)

    if key in _CACHE:
        return _CACHE[key]

    file_path = QUESTIONS_DIR / f"{key}.json"

    if not file_path.exists():
        print(f"QUESTION BANK: file not found -> {file_path}")
        _CACHE[key] = []
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        if not isinstance(data, list):
            data = []

        _CACHE[key] = data
        return data

    except Exception as error:  # malformed JSON should not crash the API
        print(f"QUESTION BANK: failed to load {file_path}: {error}")
        _CACHE[key] = []
        return []


def get_random_question(category: str, difficulty: str) -> dict | None:
    """Return one random question dict for the category/difficulty, or None."""
    questions = load_questions(category, difficulty)

    if not questions:
        return None

    return random.choice(questions)


def get_question_by_id(question_id: str) -> dict | None:
    """Look up a single question (grammar/vocab) or reading sub-question by id."""
    if not question_id:
        return None

    for file_path in QUESTIONS_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            continue

        for item in data:
            if item.get("id") == question_id:
                return item

            # Reading passages hold nested questions with their own ids.
            for sub in item.get("questions", []) or []:
                if sub.get("id") == question_id:
                    return sub

    return None


def hydrate(question: dict, category: str, difficulty: str) -> dict:
    """Ensure a question dict carries section/difficulty/estimated range fields."""
    cat = normalize_category(category)
    diff = normalize_difficulty(difficulty)

    enriched = dict(question)
    enriched.setdefault("section", cat)
    enriched.setdefault("difficulty", diff)
    enriched.setdefault("estimated_toefl_range", estimated_range_for(diff))
    enriched.setdefault("topic", cat)
    return enriched
