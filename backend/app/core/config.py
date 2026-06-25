"""
Central configuration for SMARTTOEFL AI.

Reads settings from environment variables (optionally from a `.env` file in the
backend folder) so the app can switch between an OpenAI API provider and a local
Ollama provider without code changes.
"""

import os

try:
    # python-dotenv is optional. If it is installed we load a local .env file so
    # the user can keep secrets such as OPENAI_API_KEY out of the source code.
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a convenience, not a hard dep
    pass


def _get(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip()


# ---------------------------------------------------------------------------
# LLM provider configuration
# ---------------------------------------------------------------------------
# LLM_PROVIDER controls which engine generates questions and explanations:
#   - "openai"  -> uses the OpenAI API (stable, good quality, needs an API key)
#   - "ollama"  -> uses a local Ollama model (free, offline, no API key)
#   - "dataset" -> never calls an LLM, always serves local JSON question bank
LLM_PROVIDER = _get("LLM_PROVIDER", "ollama").lower()

# OpenAI settings
OPENAI_API_KEY = _get("OPENAI_API_KEY", "")
OPENAI_MODEL = _get("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = _get("OPENAI_BASE_URL", "")  # optional custom/proxy endpoint

# Ollama settings
OLLAMA_BASE_URL = _get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = _get("OLLAMA_MODEL", "qwen2.5:1.5b")


# ---------------------------------------------------------------------------
# RAG configuration
# ---------------------------------------------------------------------------
# When enabled, the knowledge dataset (Chroma vector store) is used to ground
# AI-generated questions and AI Tutor explanations with real TOEFL material.
def _get_bool(name: str, default: bool) -> bool:
    value = _get(name, "")
    if value == "":
        return default
    return value.lower() in ("1", "true", "yes", "on")


USE_RAG = _get_bool("USE_RAG", True)

try:
    RAG_TOP_K = int(_get("RAG_TOP_K", "3"))
except ValueError:
    RAG_TOP_K = 3


# ---------------------------------------------------------------------------
# TOEFL difficulty mapping
# ---------------------------------------------------------------------------
# Maps each difficulty level to an estimated TOEFL ITP score range. Used to
# enrich generated questions and to label them in the UI.
DIFFICULTY_TOEFL_RANGE = {
    "easy": "400-450",
    "intermediate": "450-520",
    "medium": "450-520",
    "advanced": "550-650",
}


def normalize_difficulty(difficulty: str) -> str:
    """Return a canonical lowercase difficulty key (easy/intermediate/advanced)."""
    value = (difficulty or "").strip().lower()
    if value in ("medium", "intermediate"):
        return "intermediate"
    if value in ("easy", "advanced"):
        return value
    return "easy"


def normalize_category(category: str) -> str:
    """Return a canonical lowercase category key (grammar/vocabulary/reading)."""
    value = (category or "").strip().lower()
    if value in ("grammar", "vocabulary", "reading"):
        return value
    return "grammar"


def estimated_range_for(difficulty: str) -> str:
    """Return the estimated TOEFL ITP range string for a difficulty level."""
    return DIFFICULTY_TOEFL_RANGE.get(normalize_difficulty(difficulty), "400-450")
