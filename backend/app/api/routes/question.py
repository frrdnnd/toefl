import json

from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.history import PracticeHistory
from app.services.llm_service import ask_llm
from app.services.llm_service import ask_llm_generate
from app.services.rag_service import get_context


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class QuestionRequest(BaseModel):
    category: str
    difficulty: str


class EvaluationRequest(BaseModel):
    question: str
    options: list[str]
    user_answer: str
    correct_answer: str
    category: str = "Grammar"
    difficulty: str = "Intermediate"


def get_fallback_question(category: str, difficulty: str):
    normalized_category = category.lower().strip()

    fallback_questions = {
        "grammar": {
            "question": "Choose the correct sentence.",
            "options": [
                "A. She go to school.",
                "B. She goes to school.",
                "C. She going to school.",
                "D. She gone to school."
            ],
            "answer": "B",
            "explanation": "Singular subject uses a verb with s/es."
        },
        "vocabulary": {
            "question": "Choose the closest meaning of the word 'essential'.",
            "options": [
                "A. Unnecessary",
                "B. Important",
                "C. Difficult",
                "D. Temporary"
            ],
            "answer": "B",
            "explanation": "'Essential' means very important or necessary."
        },
        "reading": {
            "question": (
                "Read the sentence: 'Many students prefer online classes "
                "because they offer flexibility.' What is the main reason "
                "students prefer online classes?"
            ),
            "options": [
                "A. They are more difficult.",
                "B. They offer flexibility.",
                "C. They require more books.",
                "D. They are always free."
            ],
            "answer": "B",
            "explanation": (
                "The sentence states that students prefer online classes "
                "because they offer flexibility."
            )
        },
        "listening": {
            "question": (
                "A professor says: 'The assignment is due next Monday, "
                "not this Friday.' When is the assignment due?"
            ),
            "options": [
                "A. This Friday",
                "B. Next Monday",
                "C. Tomorrow",
                "D. Next Friday"
            ],
            "answer": "B",
            "explanation": (
                "The professor clearly says the assignment is due next Monday."
            )
        },
        "speaking": {
            "question": (
                "Which response best answers this TOEFL speaking prompt: "
                "'Describe a place you like to study and explain why.'"
            ),
            "options": [
                "A. I like studying in the library because it is quiet and helps me focus.",
                "B. I went to the library yesterday.",
                "C. Studying is sometimes difficult.",
                "D. My school has many classrooms."
            ],
            "answer": "A",
            "explanation": (
                "Option A directly describes a study place and gives a reason."
            )
        }
    }

    selected_question = fallback_questions.get(
        normalized_category,
        fallback_questions["grammar"]
    )

    return {
        **selected_question,
        "difficulty": difficulty,
        "category": category
    }


def clean_ai_json_response(response: str):
    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "")
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()

    start_index = cleaned.find("{")
    end_index = cleaned.rfind("}")

    if start_index != -1 and end_index != -1:
        cleaned = cleaned[start_index:end_index + 1]

    cleaned = "".join(
        ch
        for ch in cleaned
        if ch in "\n\r\t" or ord(ch) >= 0x20
    )

    return json.loads(cleaned)


@router.post("/generate-question")
def generate_question(payload: QuestionRequest):
    try:
        context = get_context(payload.category, payload.category)
    except Exception as e:
        print("RAG CONTEXT ERROR:", e)
        context = ""

    prompt = f"""
You are a professional TOEFL tutor AI.

Use the TOEFL material below as reference.

TOEFL MATERIAL:
{context}

TASK:
Generate exactly 1 TOEFL {payload.category} question.

Difficulty:
{payload.difficulty}

STRICT RULES:
- The question MUST be about this category: {payload.category}
- The difficulty MUST be: {payload.difficulty}
- Generate exactly 4 answer options
- Each option MUST start with A., B., C., or D.
- The answer field MUST contain only one letter: A, B, C, or D
- Add a short explanation
- Return ONLY valid JSON
- Do NOT include markdown
- Do NOT include text outside JSON

CATEGORY GUIDE:
- Grammar: ask about sentence structure, tense, subject-verb agreement, prepositions, clauses, or grammar correction.
- Vocabulary: ask about meaning, synonym, antonym, word usage, or context vocabulary.
- Reading: include a short passage, then ask about main idea, inference, detail, purpose, or reference.
- Listening: create a short spoken conversation or lecture situation, then ask a listening comprehension question.
- Speaking: create a TOEFL speaking prompt or choose the best spoken response.

JSON FORMAT:
{{
  "question": "...",
  "options": [
    "A. ...",
    "B. ...",
    "C. ...",
    "D. ..."
  ],
  "answer": "A",
  "explanation": "..."
}}
"""

    try:
        response = ask_llm_generate(prompt)
        parsed = clean_ai_json_response(response)

        required_keys = [
            "question",
            "options",
            "answer",
            "explanation"
        ]

        for key in required_keys:
            if key not in parsed:
                raise ValueError(f"Missing key from AI response: {key}")

        if not isinstance(parsed["options"], list):
            raise ValueError("Options must be a list")

        if len(parsed["options"]) != 4:
            raise ValueError("Options must contain exactly 4 choices")

        parsed["answer"] = str(parsed["answer"]).strip().upper()[0]

        if parsed["answer"] not in ["A", "B", "C", "D"]:
            raise ValueError("Answer must be A, B, C, or D")

        parsed["difficulty"] = payload.difficulty
        parsed["category"] = payload.category

        return parsed

    except Exception as e:
        print("QUESTION GENERATION ERROR:", e)

        return get_fallback_question(
            category=payload.category,
            difficulty=payload.difficulty
        )


@router.post("/evaluate-answer")
def evaluate_answer(
    payload: EvaluationRequest,
    db: Session = Depends(get_db)
):
    correct_option = next(
        (
            opt for opt in payload.options
            if opt.startswith(payload.correct_answer)
        ),
        payload.correct_answer
    )

    parsed = ask_llm(
        question=payload.question,
        options=payload.options,
        user_answer=payload.user_answer,
        correct_answer=correct_option
    )

    is_correct = (
        payload.user_answer.strip().upper()
        == payload.correct_answer.strip().upper()
    )

    if not isinstance(parsed, dict):
        parsed = {
            "correct_answer": correct_option,
            "translation": "Translation unavailable.",
            "explanation": "AI explanation unavailable.",
            "explanation_id": "Penjelasan AI tidak tersedia.",
            "why_wrong": "Could not analyze answer.",
            "why_wrong_id": "Tidak dapat menganalisis jawaban.",
            "grammar_tip": "Review grammar fundamentals.",
            "grammar_tip_id": "Tinjau dasar-dasar tata bahasa.",
            "toefl_tip": "Practice more TOEFL questions.",
            "toefl_tip_id": "Praktik lebih banyak soal TOEFL."
        }

    parsed.setdefault("correct_answer", correct_option)
    parsed.setdefault("translation", "Translation unavailable.")
    parsed.setdefault("explanation", "AI explanation unavailable.")
    parsed.setdefault("explanation_id", "Penjelasan AI tidak tersedia.")
    parsed.setdefault("why_wrong", "Could not analyze answer.")
    parsed.setdefault("why_wrong_id", "Tidak dapat menganalisis jawaban.")
    parsed.setdefault("grammar_tip", "Review grammar fundamentals.")
    parsed.setdefault("grammar_tip_id", "Tinjau dasar-dasar tata bahasa.")
    parsed.setdefault("toefl_tip", "Practice more TOEFL questions.")
    parsed.setdefault("toefl_tip_id", "Praktik lebih banyak soal TOEFL.")

    history = PracticeHistory(
        category=payload.category,
        difficulty=payload.difficulty,
        question=payload.question,
        user_answer=payload.user_answer,
        correct_answer=correct_option,
        is_correct=is_correct,
        analysis=parsed.get("explanation", ""),
        grammar_tip=parsed.get("grammar_tip", ""),
        improvement=parsed.get("toefl_tip", ""),
        weakness_detected=payload.category
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "is_correct": is_correct,
        "correct_answer": parsed.get("correct_answer", ""),
        "translation": parsed.get("translation", ""),
        "explanation": parsed.get("explanation", ""),
        "explanation_id": parsed.get("explanation_id", ""),
        "why_wrong": parsed.get("why_wrong", ""),
        "why_wrong_id": parsed.get("why_wrong_id", ""),
        "grammar_tip": parsed.get("grammar_tip", ""),
        "grammar_tip_id": parsed.get("grammar_tip_id", ""),
        "toefl_tip": parsed.get("toefl_tip", ""),
        "toefl_tip_id": parsed.get("toefl_tip_id", "")
    }
