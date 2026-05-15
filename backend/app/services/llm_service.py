import ollama
import json

MODEL = "qwen2:1.5b"


# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
You are a friendly TOEFL tutor for Indonesian students.

Always explain answers clearly and simply.

Return ONLY valid JSON.

Do NOT return markdown.
Do NOT use ```json.
Do NOT add extra text before JSON.

Required JSON format:

{
  "correct_answer": "",
  "translation": "",
  "explanation": "",
  "why_wrong": "",
  "grammar_tip": "",
  "toefl_tip": ""
}

IMPORTANT:
- translation MUST be Indonesian language
- explanation MUST be short
- explanation maximum 3 sentences
- grammar_tip maximum 2 sentences
- toefl_tip maximum 2 sentences

Rules:
- Use simple English
- Beginner friendly
- Educational but concise
- Encourage the student
- Natural teacher tone
- Avoid robotic wording
- Keep explanations short and clear
"""


# =========================
# ASK LLM
# =========================

def ask_llm(
    question,
    options,
    user_answer,
    correct_answer
):

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
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response["message"]["content"].strip()

        # =========================
        # DEBUG OUTPUT
        # =========================

        print("\n================ AI RESPONSE ================\n")
        print(content)
        print("\n============================================\n")

        # =========================
        # CLEAN MARKDOWN
        # =========================

        if "```json" in content:

            content = content.replace(
                "```json",
                ""
            )

        if "```" in content:

            content = content.replace(
                "```",
                ""
            )

        content = content.strip()

        # =========================
        # PARSE JSON
        # =========================

        try:

            parsed = json.loads(content)

            return {
                "correct_answer": parsed.get(
                    "correct_answer",
                    correct_answer
                ),

                "translation": parsed.get(
                    "translation",
                    "Terjemahan tidak tersedia."
                ),

                "explanation": parsed.get(
                    "explanation",
                    "Penjelasan tidak tersedia."
                ),

                "why_wrong": parsed.get(
                    "why_wrong",
                    "Analisis jawaban tidak tersedia."
                ),

                "grammar_tip": parsed.get(
                    "grammar_tip",
                    "Pelajari kembali grammar dasar."
                ),

                "toefl_tip": parsed.get(
                    "toefl_tip",
                    "Latihan TOEFL lebih banyak."
                )
            }

        except Exception as json_error:

            print("JSON PARSE ERROR:", json_error)

            return {
                "correct_answer": correct_answer,

                "translation": (
                    "Terjemahan tidak tersedia."
                ),

                "explanation": content,

                "why_wrong": (
                    "AI menghasilkan format JSON tidak valid."
                ),

                "grammar_tip": (
                    "Pelajari kembali grammar dasar."
                ),

                "toefl_tip": (
                    "Latihan TOEFL lebih banyak."
                )
            }

    except Exception as e:

        print("OLLAMA ERROR:", e)

        return {
            "correct_answer": correct_answer,

            "translation": (
                "Terjemahan tidak tersedia."
            ),

            "explanation": (
                "AI explanation unavailable."
            ),

            "why_wrong": (
                "Could not analyze answer."
            ),

            "grammar_tip": (
                "Check subject and verb agreement."
            ),

            "toefl_tip": (
                "Focus on grammar structure carefully."
            )
        }