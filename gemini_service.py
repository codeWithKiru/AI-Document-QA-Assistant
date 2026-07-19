import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
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

        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content

    except Exception as e:

        return f"ERROR:\n{str(e)}"

        #error = str(e)

        #if "429" in error:
           # return "⚠️ Daily Gemini API quota reached. Please try again later."

        #elif "404" in error:
           # return "⚠️ Gemini model not found."

        #elif "connection" in error.lower():
            #return "⚠️ Unable to connect to Gemini."

        #return "⚠️ Something went wrong. Please try again later."