import ollama
import json

# =========================
# MODEL
# =========================

MODEL = "gemma:2b"

# kalau mau lebih bagus nanti:
# MODEL = "phi3:mini"


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
        # DEBUG AI OUTPUT
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

                "correct_answer": (
                    parsed.get("correct_answer")
                    or correct_answer
                ),

                "translation": (
                    parsed.get("translation")
                    or f"Jawaban yang benar adalah {correct_answer}."
                ),

                "explanation": (
                    parsed.get("explanation")
                    or (
                        "This answer is correct based on "
                        "English grammar rules."
                    )
                ),

                "why_wrong": (
                    parsed.get("why_wrong")
                    or (
                        "Your answer does not match "
                        "the correct grammar structure."
                    )
                ),

                "grammar_tip": (
                    parsed.get("grammar_tip")
                    or (
                        "Review subject and verb agreement."
                    )
                ),

                "toefl_tip": (
                    parsed.get("toefl_tip")
                    or (
                        "Practice grammar patterns regularly."
                    )
                )
            }

        except Exception as json_error:

            print("JSON PARSE ERROR:", json_error)

            return {

                "correct_answer": correct_answer,

                "translation": (
                    f"Jawaban yang benar adalah "
                    f"{correct_answer}."
                ),

                "explanation": (
                    "This answer follows standard "
                    "English grammar structure."
                ),

                "why_wrong": (
                    "Your answer does not match "
                    "the correct grammar structure."
                ),

                "grammar_tip": (
                    "Review subject and verb agreement."
                ),

                "toefl_tip": (
                    "Practice grammar patterns regularly."
                )
            }

    except Exception as e:

        print("OLLAMA ERROR:", e)

        return {

            "correct_answer": correct_answer,

            "translation": (
                f"Jawaban yang benar adalah "
                f"{correct_answer}."
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
    
def ask_llm_generate(prompt: str):
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
You are a professional TOEFL question generator.

Return ONLY valid JSON.
Do NOT return markdown.
Do NOT use ```json.
Do NOT add extra text before or after JSON.

Required JSON format:
{
  "question": "",
  "options": [
    "A. ...",
    "B. ...",
    "C. ...",
    "D. ..."
  ],
  "answer": "A",
  "explanation": ""
}
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response["message"]["content"].strip()

        print("\n================ AI GENERATE RESPONSE ================\n")
        print(content)
        print("\n======================================================\n")

        return content

    except Exception as e:
        print("OLLAMA GENERATE ERROR:", e)
        return ""