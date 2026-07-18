from gemini_service import generate_answer


def generate_document_insights(chunks):
    """
    Generates AI-powered insights for the uploaded documents.
    """

    prompt = """
Analyze the uploaded document and return the result in exactly this format.

SUMMARY:
(Write a short 3-5 line summary.)

SKILLS:
(List the top technical and soft skills separated by commas.)

KEY TOPICS:
(List the important topics separated by commas.)

READING TIME:
(Estimate the reading time in minutes only.)

Do not add any extra explanation.
"""

    response = generate_answer(prompt, chunks)

    return response