import ollama

MODEL = "qwen2:1.5b"


def ask_llm(prompt: str):

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:

        print("OLLAMA ERROR:", e)

        return """
{
  "question": "Fallback AI question.",
  "options": [
    "A. Example A",
    "B. Example B",
    "C. Example C",
    "D. Example D"
  ],
  "answer": "A",
  "explanation": "Fallback response."
}
"""