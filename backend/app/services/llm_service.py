import json

import ollama


MODEL = "qwen2.5:1.5b"


SYSTEM_PROMPT_EVALUATION = """
You are a TOEFL tutor. Give feedback in JSON format.

Rules:
1. Return ONLY JSON (no markdown, no extra text)
2. Provide English and Indonesian explanations
3. Keep explanations short and clear
4. Use simple language

JSON format:
{
  "correct_answer": "X",
  "translation": "Indonesian translation of answer",
  "explanation": "Why this answer is correct (English, max 2 sentences)",
  "explanation_id": "Mengapa jawaban ini benar (Bahasa Indonesia, max 2 kalimat)",
  "why_wrong": "Why student answer was wrong (English, max 2 sentences)",
  "why_wrong_id": "Mengapa jawaban siswa salah (Bahasa Indonesia, max 2 kalimat)",
  "grammar_tip": "Grammar rule to remember (English, max 1 sentence)",
  "grammar_tip_id": "Aturan tata bahasa (Bahasa Indonesia, max 1 kalimat)",
  "toefl_tip": "Test strategy (English, max 1 sentence)",
  "toefl_tip_id": "Strategi test (Bahasa Indonesia, max 1 kalimat)"
}
"""


SYSTEM_PROMPT_GENERATION = """
You are a friendly TOEFL tutor for Indonesian students.

Generate only one TOEFL-style question in JSON.

Do NOT return markdown.
Do NOT use ```json.
Do NOT add extra text before or after the JSON.

Required JSON format:
{
  "question": "...",
  "options": [
    "A. ...",
    "B. ...",
    "C. ...",
    "D. ..."
  ],
  "answer": "A",
  "explanation": "..."
}
"""


def _clean_json_text(content: str) -> str:
    cleaned = content.strip()

    if "```json" in cleaned:
        cleaned = cleaned.replace("```json", "")

    if "```" in cleaned:
        cleaned = cleaned.replace("```", "")

    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]

    return "".join(
        ch
        for ch in cleaned
        if ch in "\n\r\t" or ord(ch) >= 0x20
    ).strip()


def ask_llm(question, options, user_answer, correct_answer):
    prompt = f"""
Question:
{question}

Options:
{options}

Student Answer:
{user_answer}

Correct Answer:
{correct_answer}

TASK:
Explain:
- why the answer is correct
- why the student's answer is wrong
- grammar explanation
- TOEFL strategy
- Indonesian translation

Return valid JSON only.
"""

    try:
        response = ollama.chat(
            model=MODEL,
            options={
                "temperature": 0.2,
                "num_predict": 500
            },
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_EVALUATION
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = _clean_json_text(response["message"]["content"])

        try:
            parsed = json.loads(content)
        except Exception as json_error:
            print("JSON PARSE ERROR:", json_error, "Content:", content[:200])
            parsed = {}

        return {
            "correct_answer": (
                (parsed.get("correct_answer") or "").strip()
                or correct_answer
            ),
            "translation": (
                (parsed.get("translation") or "").strip()
                or f"Jawaban yang benar adalah {correct_answer}."
            ),
            "explanation": (
                (parsed.get("explanation") or "").strip()
                or "This answer is correct based on English grammar rules."
            ),
            "explanation_id": (
                (parsed.get("explanation_id") or "").strip()
                or "Jawaban ini benar berdasarkan aturan tata bahasa Inggris."
            ),
            "why_wrong": (
                (parsed.get("why_wrong") or "").strip()
                or "Your answer does not match the correct grammar structure."
            ),
            "why_wrong_id": (
                (parsed.get("why_wrong_id") or "").strip()
                or "Jawabanmu tidak sesuai dengan struktur tata bahasa yang benar."
            ),
            "grammar_tip": (
                (parsed.get("grammar_tip") or "").strip()
                or "Review subject and verb agreement."
            ),
            "grammar_tip_id": (
                (parsed.get("grammar_tip_id") or "").strip()
                or "Tinjau kesesuaian subjek dan verba."
            ),
            "toefl_tip": (
                (parsed.get("toefl_tip") or "").strip()
                or "Practice grammar patterns regularly."
            ),
            "toefl_tip_id": (
                (parsed.get("toefl_tip_id") or "").strip()
                or "Praktik pola tata bahasa secara teratur."
            )
        }

    except Exception as e:
        print("OLLAMA ERROR:", e)

        return {
            "correct_answer": correct_answer,
            "translation": f"Jawaban yang benar adalah {correct_answer}.",
            "explanation": "AI explanation unavailable.",
            "explanation_id": "Penjelasan AI tidak tersedia.",
            "why_wrong": "Could not analyze answer.",
            "why_wrong_id": "Tidak dapat menganalisis jawaban.",
            "grammar_tip": "Check subject and verb agreement.",
            "grammar_tip_id": "Periksa kesesuaian subjek dan verba.",
            "toefl_tip": "Focus on grammar structure carefully.",
            "toefl_tip_id": "Fokus pada struktur tata bahasa dengan cermat."
        }


def ask_llm_generate(prompt: str):
    try:
        response = ollama.chat(
            model=MODEL,
            options={
                "temperature": 0.2,
                "num_predict": 300
            },
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_GENERATION
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return _clean_json_text(response["message"]["content"])

    except Exception as e:
        print("OLLAMA GENERATE ERROR:", e)
        return ""
