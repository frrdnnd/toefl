"""
LLM service abstraction for SMARTTOEFL AI.

Supports two interchangeable providers (OpenAI API and local Ollama) plus a
deterministic dataset fallback. Public functions used by the API:

    generate_question(category, difficulty, mode)   -> (data, source)
    generate_explanation(question, options, ...)    -> bilingual feedback dict
    analyze_weakness(history)                        -> weakness summary dict

If a provider errors or returns invalid data, the service never crashes: it
falls back to the local JSON question bank and to safe default explanations.
"""

import json

from app.core import config
from app.core.config import normalize_category
from app.core.config import normalize_difficulty
from app.core.config import estimated_range_for
from app.services import question_bank


# ---------------------------------------------------------------------------
# Low-level provider dispatch
# ---------------------------------------------------------------------------

_openai_client = None
_ollama_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI  # lazy import: only needed for openai provider

        kwargs = {"api_key": config.OPENAI_API_KEY}
        if config.OPENAI_BASE_URL:
            kwargs["base_url"] = config.OPENAI_BASE_URL
        _openai_client = OpenAI(**kwargs)
    return _openai_client


def _get_ollama_client():
    global _ollama_client
    if _ollama_client is None:
        from ollama import Client  # lazy import: only needed for ollama provider

        _ollama_client = Client(host=config.OLLAMA_BASE_URL)
    return _ollama_client


def llm_available() -> bool:
    """True if a real LLM provider is configured (not the pure dataset mode)."""
    if config.LLM_PROVIDER == "openai":
        return bool(config.OPENAI_API_KEY)
    if config.LLM_PROVIDER == "ollama":
        return True
    return False


def _chat(system_prompt, user_prompt, temperature=0.4, max_tokens=700, json_mode=True):
    """Send a system+user prompt to the configured provider, return raw text.

    Raises an exception if the provider is unavailable or fails; callers are
    expected to catch and fall back to the dataset.
    """
    provider = config.LLM_PROVIDER

    if provider == "openai":
        if not config.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set")

        client = _get_openai_client()
        request = {
            "model": config.OPENAI_MODEL,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if json_mode:
            request["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**request)
        return response.choices[0].message.content or ""

    if provider == "ollama":
        client = _get_ollama_client()
        response = client.chat(
            model=config.OLLAMA_MODEL,
            format="json" if json_mode else "",
            options={"temperature": temperature, "num_predict": max_tokens},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response["message"]["content"]

    raise RuntimeError(f"No usable LLM provider for LLM_PROVIDER={provider!r}")


def _parse_json(raw: str):
    """Extract and parse a JSON object from a possibly noisy LLM response."""
    cleaned = (raw or "").strip()

    if "```json" in cleaned:
        cleaned = cleaned.replace("```json", "")
    if "```" in cleaned:
        cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]

    cleaned = "".join(
        ch for ch in cleaned if ch in "\n\r\t" or ord(ch) >= 0x20
    )

    return json.loads(cleaned)


# ---------------------------------------------------------------------------
# RAG retrieval (knowledge grounding)
# ---------------------------------------------------------------------------

def _retrieve_context(category: str, query: str) -> str:
    """Fetch grounding context from the RAG vector store, or "" if disabled/failed."""
    if not config.USE_RAG:
        return ""
    try:
        from app.services import rag_service  # lazy: avoids loading the model unless used

        return rag_service.get_context(query, category, k=config.RAG_TOP_K)
    except Exception as error:
        print("RAG retrieve error:", error)
        return ""


def _with_reference(prompt: str, context: str) -> str:
    """Prepend RAG reference material to a prompt as inspiration (not to copy)."""
    if not context:
        return prompt
    snippet = context[:1500]
    return (
        "Use the following authentic TOEFL reference material as inspiration for the "
        "academic style, vocabulary, and topic. Do NOT copy it verbatim; produce an "
        "original item.\n\nREFERENCE MATERIAL:\n"
        f"{snippet}\n\n----\n\n{prompt}"
    )


# ---------------------------------------------------------------------------
# Prompt generators (one per category)
# ---------------------------------------------------------------------------

_GRAMMAR_FOCUS = {
    "easy": (
        "basic subject-verb agreement, common verb tenses, pronoun reference, "
        "and basic prepositions"
    ),
    "intermediate": (
        "passive voice, relative clauses, noun clauses, parallel structure, "
        "and comparisons"
    ),
    "advanced": (
        "inversion, the subjunctive, reduced adjective clauses, reduced adverb "
        "clauses, complex parallel structure, conditional sentences, and "
        "advanced subject-verb agreement"
    ),
}

_VOCAB_FOCUS = {
    "easy": "common academic words",
    "intermediate": "moderately academic words",
    "advanced": (
        "abstract academic words such as ambiguous, skeptical, substantial, "
        "inevitable, preliminary, diminish, acquire, fluctuate, significant, "
        "and consequently"
    ),
}

_READING_LENGTH = {
    "easy": "100-150 words",
    "intermediate": "180-250 words",
    "advanced": "250-350 words",
}


def _grammar_prompt(difficulty: str, toefl_range: str, seed: dict | None) -> str:
    seed_text = ""
    if seed:
        seed_text = (
            "\nHere is an example question of the right level for inspiration. "
            "Create a NEW and different question, do not copy it:\n"
            f"{json.dumps(seed, ensure_ascii=False)}\n"
        )

    return f"""Generate ONE TOEFL ITP-style grammar question.

Requirements:
- Difficulty: {difficulty}
- Estimated TOEFL range: {toefl_range}
- Multiple choice with exactly four options A, B, C, D
- Only one correct answer
- Use academic English
- Avoid overly simple questions
- The question must resemble TOEFL Structure and Written Expression style
  (a sentence with a blank to complete, or an error to identify).
- For this difficulty, focus on: {_GRAMMAR_FOCUS.get(difficulty, _GRAMMAR_FOCUS['easy'])}.
{seed_text}
Return JSON only with this exact shape:
{{
  "section": "grammar",
  "difficulty": "{difficulty}",
  "estimated_toefl_range": "{toefl_range}",
  "topic": "...",
  "question": "...",
  "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
  "answer": "A",
  "explanation": "..."
}}"""


def _vocabulary_prompt(difficulty: str, toefl_range: str, seed: dict | None) -> str:
    seed_text = ""
    if seed:
        seed_text = (
            "\nExample of the right level (create a NEW, different one):\n"
            f"{json.dumps(seed, ensure_ascii=False)}\n"
        )

    return f"""Generate ONE TOEFL ITP-style vocabulary question.

Requirements:
- Difficulty: {difficulty}
- Estimated TOEFL range: {toefl_range}
- Use academic vocabulary.
- The question must ask for the closest meaning of an underlined or quoted word
  used inside a short academic sentence.
- Multiple choice with exactly four options A, B, C, D.
- Only one correct answer.
- Avoid basic words such as happy, sad, big, small.
- For this difficulty, use {_VOCAB_FOCUS.get(difficulty, _VOCAB_FOCUS['easy'])}.
{seed_text}
Return JSON only with this exact shape:
{{
  "section": "vocabulary",
  "difficulty": "{difficulty}",
  "estimated_toefl_range": "{toefl_range}",
  "topic": "vocabulary in context",
  "question": "...",
  "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
  "answer": "A",
  "explanation": "..."
}}"""


def _reading_prompt(difficulty: str, toefl_range: str, seed: dict | None) -> str:
    seed_hint = ""
    if seed and seed.get("topic"):
        seed_hint = (
            f"\n- Take inspiration from this academic topic area: "
            f"\"{seed['topic']}\" (write an ORIGINAL passage, do not copy)."
        )

    return f"""Generate ONE TOEFL ITP-style reading passage with questions.

Requirements:
- Difficulty: {difficulty}
- Estimated TOEFL range: {toefl_range}
- Choose an academic topic (science, history, environment, society, technology).{seed_hint}
- Passage length: {_READING_LENGTH.get(difficulty, _READING_LENGTH['easy'])}.
- Generate exactly 5 questions.
- The five question types MUST be: main_idea, detail, vocabulary_in_context,
  inference, and reference.
- Each question has exactly four options A, B, C, D and only one correct answer.
- Include a clear explanation for every answer.

Return JSON only with this exact shape:
{{
  "section": "reading",
  "difficulty": "{difficulty}",
  "estimated_toefl_range": "{toefl_range}",
  "topic": "...",
  "passage": "...",
  "questions": [
    {{
      "type": "main_idea",
      "question": "...",
      "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
      "answer": "C",
      "explanation": "..."
    }}
  ]
}}"""


_GENERATION_SYSTEM = (
    "You are an expert TOEFL ITP item writer. You create academic, "
    "test-realistic questions and you reply with valid JSON only, with no "
    "markdown and no text outside the JSON object."
)


# ---------------------------------------------------------------------------
# Validation / normalization of generated questions
# ---------------------------------------------------------------------------

def _normalize_options(options) -> dict:
    """Coerce options into a {A,B,C,D} dict, accepting list or dict input."""
    if isinstance(options, dict):
        result = {k.strip().upper(): str(v).strip() for k, v in options.items()}
    elif isinstance(options, list):
        result = {}
        letters = ["A", "B", "C", "D"]
        for index, value in enumerate(options[:4]):
            text = str(value).strip()
            # strip a leading "A." / "B)" style prefix if present
            if len(text) > 2 and text[0].upper() in letters and text[1] in ".)":
                text = text[2:].strip()
            result[letters[index]] = text
    else:
        raise ValueError("options must be a dict or list")

    for letter in ("A", "B", "C", "D"):
        if letter not in result or not result[letter]:
            raise ValueError("options must contain non-empty A, B, C, D")

    return {letter: result[letter] for letter in ("A", "B", "C", "D")}


def _normalize_answer(answer) -> str:
    letter = str(answer).strip().upper()
    letter = letter[0] if letter else ""
    if letter not in ("A", "B", "C", "D"):
        raise ValueError("answer must be A, B, C, or D")
    return letter


def _normalize_mc_question(data: dict, category: str, difficulty: str) -> dict:
    toefl_range = estimated_range_for(difficulty)
    return {
        "section": category,
        "difficulty": difficulty,
        "estimated_toefl_range": data.get("estimated_toefl_range") or toefl_range,
        "topic": (data.get("topic") or category).strip(),
        "question": str(data["question"]).strip(),
        "options": _normalize_options(data["options"]),
        "answer": _normalize_answer(data["answer"]),
        "explanation": str(data.get("explanation", "")).strip(),
    }


def _normalize_reading(data: dict, difficulty: str) -> dict:
    toefl_range = estimated_range_for(difficulty)
    raw_questions = data.get("questions")
    if not isinstance(raw_questions, list) or not raw_questions:
        raise ValueError("reading must include a non-empty questions list")

    questions = []
    for index, item in enumerate(raw_questions, start=1):
        questions.append({
            "id": item.get("id") or f"reading_ai_q{index}",
            "type": (item.get("type") or "detail").strip(),
            "question": str(item["question"]).strip(),
            "options": _normalize_options(item["options"]),
            "answer": _normalize_answer(item["answer"]),
            "explanation": str(item.get("explanation", "")).strip(),
        })

    passage = str(data.get("passage", "")).strip()
    if not passage:
        raise ValueError("reading must include a passage")

    return {
        "section": "reading",
        "difficulty": difficulty,
        "estimated_toefl_range": data.get("estimated_toefl_range") or toefl_range,
        "topic": (data.get("topic") or "reading").strip(),
        "passage": passage,
        "questions": questions,
    }


def _generate_with_ai(category: str, difficulty: str, seed: dict | None):
    """Try to generate a question with the LLM. Return dict or None on failure."""
    toefl_range = estimated_range_for(difficulty)

    # Ground the prompt with authentic TOEFL material from the RAG vector store.
    topic_hint = (seed or {}).get("topic", "")
    context = _retrieve_context(
        category, f"{category} {difficulty} {topic_hint} TOEFL practice".strip()
    )
    rag_used = bool(context)

    if category == "reading":
        user_prompt = _reading_prompt(difficulty, toefl_range, seed)
        max_tokens = 1400
    elif category == "vocabulary":
        user_prompt = _vocabulary_prompt(difficulty, toefl_range, seed)
        max_tokens = 500
    else:
        user_prompt = _grammar_prompt(difficulty, toefl_range, seed)
        max_tokens = 500

    user_prompt = _with_reference(user_prompt, context)

    try:
        raw = _chat(
            _GENERATION_SYSTEM,
            user_prompt,
            temperature=0.7,
            max_tokens=max_tokens,
            json_mode=True,
        )
        data = _parse_json(raw)

        if category == "reading":
            result = _normalize_reading(data, difficulty)
        else:
            result = _normalize_mc_question(data, category, difficulty)

        result["rag_used"] = rag_used
        return result

    except Exception as error:
        print("AI GENERATE ERROR:", error)
        return None


# ---------------------------------------------------------------------------
# Public API: question generation
# ---------------------------------------------------------------------------

def generate_question(category: str, difficulty: str, mode: str = "dataset"):
    """Return (question_dict, source) for the given category/difficulty/mode.

    mode:
      - "dataset" -> always serve a question from the local JSON bank
      - "ai"      -> generate with the LLM; fall back to dataset on failure
      - "hybrid"  -> use a dataset question as a seed, vary it with the LLM
    """
    category = normalize_category(category)
    difficulty = normalize_difficulty(difficulty)
    mode = (mode or "dataset").lower()

    # Pure dataset mode, or no LLM available at all.
    if mode == "dataset" or not llm_available():
        return _dataset_question(category, difficulty), "dataset"

    seed = None
    if mode == "hybrid":
        seed = question_bank.get_random_question(category, difficulty)

    ai_result = _generate_with_ai(category, difficulty, seed)
    if ai_result is not None:
        return ai_result, config.LLM_PROVIDER

    # AI failed -> graceful fallback to the local bank.
    return _dataset_question(category, difficulty), "dataset"


def _dataset_question(category: str, difficulty: str) -> dict:
    """Return a dataset (or hardcoded) question tagged with rag_used=False."""
    question = question_bank.get_random_question(category, difficulty)
    if question:
        data = question_bank.hydrate(question, category, difficulty)
    else:
        data = _hardcoded_fallback(category, difficulty)
    data["rag_used"] = False
    return data


def _hardcoded_fallback(category: str, difficulty: str) -> dict:
    """Last-resort question if the JSON bank is missing or empty."""
    toefl_range = estimated_range_for(difficulty)

    if category == "reading":
        return {
            "section": "reading",
            "difficulty": difficulty,
            "estimated_toefl_range": toefl_range,
            "topic": "online learning",
            "passage": (
                "Many students prefer online classes because they offer "
                "flexibility. Learners can study at any time and from any "
                "place, which helps those who also work or care for family "
                "members."
            ),
            "questions": [
                {
                    "id": "fallback_reading_q1",
                    "type": "detail",
                    "question": "Why do many students prefer online classes?",
                    "options": {
                        "A": "They are more difficult.",
                        "B": "They offer flexibility.",
                        "C": "They require more books.",
                        "D": "They are always free.",
                    },
                    "answer": "B",
                    "explanation": "The passage states online classes offer flexibility.",
                }
            ],
        }

    if category == "vocabulary":
        return {
            "section": "vocabulary",
            "difficulty": difficulty,
            "estimated_toefl_range": toefl_range,
            "topic": "vocabulary in context",
            "question": "The word 'essential' is closest in meaning to",
            "options": {
                "A": "unnecessary",
                "B": "important",
                "C": "difficult",
                "D": "temporary",
            },
            "answer": "B",
            "explanation": "'Essential' means very important or necessary.",
        }

    return {
        "section": "grammar",
        "difficulty": difficulty,
        "estimated_toefl_range": toefl_range,
        "topic": "subject-verb agreement",
        "question": "The committee ____ to announce its decision tomorrow.",
        "options": {
            "A": "are expected",
            "B": "is expected",
            "C": "expecting",
            "D": "expect",
        },
        "answer": "B",
        "explanation": "'The committee' is treated as singular, so 'is expected' is correct.",
    }


# ---------------------------------------------------------------------------
# Public API: answer explanation (bilingual feedback)
# ---------------------------------------------------------------------------

_EVALUATION_SYSTEM = """You are a bilingual TOEFL tutor for Indonesian students.
Return ONLY JSON (no markdown, no extra text), with short, clear explanations in
both English and Indonesian, using this exact format:
{
  "translation": "Indonesian translation of the correct answer / key idea",
  "explanation": "Why the correct answer is correct (English, max 2 sentences)",
  "explanation_id": "Mengapa jawaban benar (Bahasa Indonesia, max 2 kalimat)",
  "why_wrong": "Why the student's answer is wrong (English, max 2 sentences)",
  "why_wrong_id": "Mengapa jawaban siswa salah (Bahasa Indonesia, max 2 kalimat)",
  "grammar_tip": "One rule to remember (English, max 1 sentence)",
  "grammar_tip_id": "Satu aturan untuk diingat (Bahasa Indonesia, max 1 kalimat)",
  "toefl_tip": "One TOEFL strategy (English, max 1 sentence)",
  "toefl_tip_id": "Satu strategi TOEFL (Bahasa Indonesia, max 1 kalimat)"
}"""


def _explanation_defaults(correct_answer: str, base_explanation: str = "") -> dict:
    english = base_explanation or "This answer is correct based on TOEFL English rules."
    return {
        "correct_answer": correct_answer,
        "translation": f"Jawaban yang benar adalah {correct_answer}.",
        "explanation": english,
        "explanation_id": "Jawaban ini benar berdasarkan aturan bahasa Inggris TOEFL.",
        "why_wrong": "Your answer does not match the correct structure or meaning.",
        "why_wrong_id": "Jawabanmu tidak sesuai dengan struktur atau makna yang benar.",
        "grammar_tip": "Review the relevant TOEFL pattern carefully.",
        "grammar_tip_id": "Tinjau pola TOEFL yang relevan dengan cermat.",
        "toefl_tip": "Read every option fully before choosing.",
        "toefl_tip_id": "Baca semua pilihan dengan lengkap sebelum memilih.",
    }


def generate_explanation(
    question,
    options,
    user_answer,
    correct_answer,
    is_correct=None,
    base_explanation="",
    use_llm=True,
    category="",
):
    """Return rich bilingual feedback. Falls back to safe defaults on any error.

    Set use_llm=False for a fast, deterministic response (e.g. when grading the
    many sub-questions of a reading passage), which avoids one LLM call per item.
    When RAG is enabled, the explanation is grounded with TOEFL reference material.
    """
    defaults = _explanation_defaults(correct_answer, base_explanation)
    defaults["rag_used"] = False

    if not use_llm or not llm_available():
        return defaults

    # AI Tutor grounding: retrieve relevant TOEFL material for this question.
    context = _retrieve_context(category, f"{question} {correct_answer}")
    rag_used = bool(context)

    reference_block = ""
    if context:
        reference_block = (
            "\n\nReference material (use it to keep the explanation accurate):\n"
            f"{context[:1200]}\n"
        )

    user_prompt = f"""Question:
{question}

Options:
{json.dumps(options, ensure_ascii=False)}

Student answer: {user_answer}
Correct answer: {correct_answer}
The student was {"CORRECT" if is_correct else "INCORRECT"}.{reference_block}

Explain why the correct answer is right and, if the student was wrong, why their
choice is wrong. Add one grammar/usage tip and one TOEFL strategy tip. Provide
both English and Indonesian. Return JSON only."""

    try:
        raw = _chat(
            _EVALUATION_SYSTEM,
            user_prompt,
            temperature=0.2,
            max_tokens=500,
            json_mode=True,
        )
        parsed = _parse_json(raw)

        result = dict(defaults)
        for key in (
            "translation",
            "explanation",
            "explanation_id",
            "why_wrong",
            "why_wrong_id",
            "grammar_tip",
            "grammar_tip_id",
            "toefl_tip",
            "toefl_tip_id",
        ):
            value = parsed.get(key)
            if isinstance(value, str) and value.strip():
                result[key] = value.strip()

        # The correct answer is decided deterministically by the caller.
        result["correct_answer"] = correct_answer
        result["rag_used"] = rag_used
        return result

    except Exception as error:
        print("EXPLANATION ERROR:", error)
        return defaults


# ---------------------------------------------------------------------------
# Public API: weakness analysis (AI Tutor)
# ---------------------------------------------------------------------------

# Short, deterministic study tips keyed by topic. Used by the AI Tutor and the
# check-answer endpoint so recommendations always work, even with no LLM.
_TOPIC_RECOMMENDATIONS = {
    "inversion": "Practice inversion after negative adverbials such as Not until, Never, Rarely, and Seldom.",
    "subjunctive": "Review the subjunctive: use the base verb after insist, suggest, essential, and important.",
    "reduced adjective clause": "Practice reducing relative clauses by deleting 'who/which + be'.",
    "reduced adverb clause": "Practice reducing adverb clauses while keeping the conjunction (e.g. 'When exposed...').",
    "conditional sentence": "Review the three conditional types, including inverted forms like 'Had I known...'.",
    "passive voice": "Review passive forms (be + past participle) across different tenses.",
    "relative clause": "Practice choosing who, whom, whose, which, and that correctly.",
    "noun clause": "Practice noun clauses introduced by that, what, where, and whether.",
    "parallel structure": "Keep items in a list or after correlatives (not only...but also) in the same grammatical form.",
    "comparison": "Review comparative and superlative forms and the double comparative (the more..., the more...).",
    "subject-verb agreement": "Watch for tricky subjects: 'the number of' is singular, 'a number of' is plural.",
    "present tense": "Review third-person singular -s and habitual present usage.",
    "past tense": "Review regular and irregular simple past forms.",
    "preposition": "Review prepositions of time and place (at, on, in).",
    "pronoun reference": "Make sure every pronoun clearly matches the noun it replaces.",
    "vocabulary in context": "Review academic vocabulary and transition words; learn synonyms in context.",
    "academic vocabulary": "Build academic vocabulary daily and study words in full sentences.",
    "main_idea": "Practice finding the main idea by reading the first and last sentences of each paragraph.",
    "detail": "Practice scanning the passage for specific facts mentioned in the question.",
    "inference": "Practice inference questions by reasoning beyond what is stated directly.",
    "reference": "Practice reference questions by matching pronouns to the nouns they point to.",
}


def recommend_for_topic(topic: str, category: str = "") -> str:
    """Return a study recommendation for a topic (deterministic, always works)."""
    key = (topic or "").strip().lower()
    if key in _TOPIC_RECOMMENDATIONS:
        return _TOPIC_RECOMMENDATIONS[key]

    cat = normalize_category(category)
    if cat == "vocabulary":
        return _TOPIC_RECOMMENDATIONS["academic vocabulary"]
    if cat == "reading":
        return _TOPIC_RECOMMENDATIONS["main_idea"]
    return "Review the grammar pattern in this question and practice similar items."


def analyze_weakness(history) -> dict:
    """Summarize weak topics/categories from practice history.

    `history` is an iterable of objects/dicts with: category, topic, is_correct.
    Returns weak topics, weak categories, and concrete recommendations. This is
    computed deterministically so the AI Tutor works without any LLM.
    """
    def _attr(item, name, default=None):
        if isinstance(item, dict):
            return item.get(name, default)
        return getattr(item, name, default)

    topic_stats: dict[str, dict] = {}
    category_stats: dict[str, dict] = {}

    for item in history or []:
        is_correct = bool(_attr(item, "is_correct"))
        category = normalize_category(_attr(item, "category", "grammar"))
        topic = (_attr(item, "topic") or "").strip() or category

        c = category_stats.setdefault(category, {"total": 0, "wrong": 0})
        c["total"] += 1
        c["wrong"] += 0 if is_correct else 1

        t = topic_stats.setdefault(topic, {"total": 0, "wrong": 0, "category": category})
        t["total"] += 1
        t["wrong"] += 0 if is_correct else 1

    # Weak topics: at least one wrong answer, sorted by number of mistakes.
    weak_topics = sorted(
        (
            {
                "topic": topic,
                "category": stats["category"],
                "wrong": stats["wrong"],
                "total": stats["total"],
                "accuracy": round((stats["total"] - stats["wrong"]) / stats["total"] * 100),
            }
            for topic, stats in topic_stats.items()
            if stats["wrong"] > 0
        ),
        key=lambda entry: (entry["wrong"], -entry["accuracy"]),
        reverse=True,
    )

    recommendations = [
        recommend_for_topic(entry["topic"], entry["category"])
        for entry in weak_topics[:3]
    ]
    # De-duplicate while preserving order.
    seen = set()
    recommendations = [r for r in recommendations if not (r in seen or seen.add(r))]

    if not recommendations:
        recommendations = [
            "Great work! Keep practicing across all sections to stay sharp."
        ]

    return {
        "weak_topics": weak_topics[:5],
        "category_accuracy": {
            category: round((stats["total"] - stats["wrong"]) / stats["total"] * 100)
            for category, stats in category_stats.items()
            if stats["total"] > 0
        },
        "recommendations": recommendations,
    }
