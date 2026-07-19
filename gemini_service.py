import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

load_dotenv()

# Get API Key
api_key = os.getenv("GOOGLE_API_KEY")

# Display first 10 characters of API Key for debugging
if api_key:
    st.write("🔑 API Key:", api_key[:10] + "...")
else:
    st.error("❌ GOOGLE_API_KEY not found!")

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    google_api_key=api_key,
    temperature=0.3
)


def generate_answer(question, chunks, chat_history=None):
    context = "\n\n".join(
        [chunk["text"] for chunk in chunks]
    )

    history = ""

    if chat_history:
        for message in chat_history[-6:]:
            role = "User" if message["role"] == "user" else "Assistant"
            history += f"{role}: {message['content']}\n"

    prompt = f"""
You are an AI Document Q&A Assistant.

Use ONLY the information provided in the uploaded document.

Maintain conversation continuity using the previous conversation when it is relevant.

If the current question is a follow-up (for example: "explain more", "what about this", "why", "can you elaborate"), use the conversation history to understand what the user is referring to.

Do NOT invent information outside the uploaded document.

If the answer is directly stated, answer it.

If the answer can be reasonably inferred from the document, explain it.

Only if the document contains no relevant information at all, reply:

"I couldn't find this information in the uploaded document."

------------------------
Conversation History
------------------------

{history}

------------------------
Document
------------------------

{context}

------------------------
Current Question
------------------------

{question}

Answer:
"""

    try:
        response = llm.invoke(prompt)
        return response.content

    except Exception:
        raise