from gemini_service import generate_answer

def generate_suggested_questions(chunks):

    prompt = """
Generate 5 short questions a user might ask based on these documents.

Return only the questions.
One per line.
"""

    response = generate_answer(prompt, chunks)

    return [
        q.strip("-•1234567890. ")
        for q in response.split("\n")
        if q.strip()
    ]