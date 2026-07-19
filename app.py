import streamlit as st
import time

from io import BytesIO
from datetime import datetime

#from reportlab.platypus import SimpleDocTemplate, Paragraph
#from reportlab.lib.styles import getSampleStyleSheet

from pdf_reader import extract_text
from text_splitter import split_text
from rag import create_vector_store, retrieve_chunks
from gemini_service import generate_answer
from suggestions import generate_suggested_questions
from insights import generate_document_insights

#import langchain_google_genai
#import google.genai

#st.write("LangChain Google GenAI:", langchain_google_genai.__version__)
#st.write("Google GenAI:", google.genai.__version__)

# -------------------------------
# Create PDF Chat Export
# -------------------------------

def create_chat_pdf(messages):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "<b>AI Document Q&A Chat History</b>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            styles["Normal"]
        )
    )

    story.append(Paragraph("<br/><br/>", styles["Normal"]))

    for msg in messages:

        if msg["role"] == "user":

            story.append(
                Paragraph(
                    f"<b>👤 User:</b> {msg['content']}",
                    styles["BodyText"]
                )
            )

        else:

            story.append(
                Paragraph(
                    f"<b>🤖 Assistant:</b> {msg['content']}",
                    styles["BodyText"]
                )
            )

        story.append(
            Paragraph("<br/>", styles["Normal"])
        )

    doc.build(story)

    buffer.seek(0)

    return buffer

st.set_page_config(
    page_title="AI Document Q&A Assistant",
    page_icon="📄",
    layout="wide"
)

# -------------------------------
# Session State
# -------------------------------

defaults = {
    "messages": [],
    "vector_store": None,
    "uploaded": False,
    "total_documents": 0,
    "total_pages": 0,
    "total_chunks": 0,
    "question_count": 0,
    "suggested_questions": [],
    "document_insights": "",
    "chat_title": "New Chat",
    "chat_history": [],
    "uploader_key": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------------------
# Sidebar
# -------------------------------

with st.sidebar:

    st.title("📄 AI Document Assistant")

    if st.button("➕ New Chat", use_container_width=True):

        if st.session_state.messages:

            st.session_state.chat_history.append(
                {
                    "title": st.session_state.chat_title,
                    "messages": st.session_state.messages.copy()
                }
            )

        # Reset everything related to the current chat
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"
        st.session_state.question_count = 0

        st.session_state.uploaded = False
        st.session_state.vector_store = None
        st.session_state.total_documents = 0
        st.session_state.total_pages = 0
        st.session_state.total_chunks = 0
        st.session_state.suggested_questions = []
        st.session_state.document_insights = ""
        st.session_state.uploader_key += 1

        st.rerun()

    uploaded_files = st.file_uploader(
        "Upload PDF Documents",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"
    )

    if st.button("📥 Process Documents"):

        if uploaded_files:

            with st.spinner("Reading and processing PDFs..."):

                pages = extract_text(uploaded_files)
                chunks = split_text(pages)
                vector_store = create_vector_store(chunks)

                st.session_state.vector_store = vector_store
                st.session_state.uploaded = True
                st.session_state.messages = []

                st.session_state.total_documents = len(uploaded_files)
                st.session_state.total_pages = len(pages)
                st.session_state.total_chunks = len(chunks)
                st.session_state.question_count = 0

                if len(uploaded_files) == 1:
                    st.session_state.chat_title = uploaded_files[0].name
                else:
                    st.session_state.chat_title = f"{len(uploaded_files)} Documents"

                st.session_state.suggested_questions = (
                   generate_suggested_questions(chunks)
                )

                st.session_state.document_insights = (
                   generate_document_insights(chunks)
                )

            st.success("✅ Documents processed successfully!")
            st.info("💬 Your documents are ready. You can now ask questions below.")

        else:
            st.warning("Please upload at least one PDF.")

    st.divider()

    if st.button("🗑 Clear Chat"):

        if st.session_state.messages:

            st.session_state.chat_history.append(
                {
                    "title": st.session_state.chat_title,
                    "messages": st.session_state.messages.copy()
                }
            )

        st.session_state.messages = []
        
        st.session_state.question_count = 0

        st.rerun()

    st.divider()

    search_chat = st.text_input(
        "🔍 Search Chats",
        placeholder="Search by chat title..."
    )

    st.subheader("🕒 Recent Chats")

    if not st.session_state.chat_history:

        st.info("No chats yet")

    else:

        filtered_chats = [
            chat for chat in reversed(st.session_state.chat_history)
            if search_chat.lower() in chat["title"].lower()
        ]

        for i, chat in enumerate(filtered_chats):

            col1, col2 = st.columns([5, 1])

            with col1:

                if st.button(
                    f"📄 {chat['title']}",
                    key=f"history_{i}",
                    use_container_width=True
                ):

                    st.session_state.messages = chat["messages"].copy()
                    st.session_state.chat_title = chat["title"]
                    st.session_state.question_count = sum(
                        1 for msg in chat["messages"]
                        if msg["role"] == "user"
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "🗑",
                    key=f"delete_{i}"
                ):

                    st.session_state.chat_history.pop(
                        len(st.session_state.chat_history) - 1 - i
                    )

                    st.rerun()

# -------------------------------
# Main Page
# -------------------------------

st.title("🤖 AI Document Q&A Assistant")

st.subheader(f"📂 {st.session_state.chat_title}")

st.caption(
    "Ask questions about your uploaded PDF documents using Gemini + FAISS."
)

# -------------------------------
# Dashboard
# -------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("📄 Documents", st.session_state.total_documents)
col2.metric("📑 Pages", st.session_state.total_pages)
col3.metric("🧩 Chunks", st.session_state.total_chunks)
col4.metric("💬 Questions", st.session_state.question_count)

st.divider()

# -------------------------------
# AI Document Insights
# -------------------------------

if st.session_state.document_insights:

    with st.expander("📊 AI Document Insights", expanded=True):

        st.markdown(st.session_state.document_insights)

st.divider()

# -------------------------------
# Previous Chat
# -------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        role = "👤 User" if message["role"] == "user" else "🤖 Assistant"

        timestamp = message.get("time", "")

        st.caption(f"{role} • {timestamp}")

        st.markdown(message["content"])

        if message["role"] == "assistant" and "sources" in message:

            with st.expander("📚 Retrieved Sources"):

                for source in message["sources"]:

                    if isinstance(source, dict):

                        st.markdown(
                            f"**📄 {source.get('filename','Document')}**"
                        )

                        st.caption(
                            f"Page {source.get('page','Unknown')}"
                        )

                        st.write(
                            source.get("text", "")
                        )

                    else:

                        st.write(source)

                    st.divider()
# -------------------------------
# Quick AI Actions
# -------------------------------
actions_disabled = not st.session_state.uploaded

st.subheader("⚡ Quick AI Actions")

col1, col2, col3, col4, col5 = st.columns(5)

selected_prompt = None

with col1:

    if st.button("📄 Summarize", disabled=actions_disabled):

        selected_prompt = "Summarize this document."

with col2:

    if st.button("💼 Extract Skills", disabled=actions_disabled):

        selected_prompt = (
            "List all technical and soft skills mentioned in this document."
        )

with col3:

    if st.button("❓ Interview Questions", disabled=actions_disabled):

        selected_prompt = (
            "Generate interview questions based on this document."
        )

with col4:

    if st.button("📌 Key Points", disabled=actions_disabled):

        selected_prompt = (
            "What are the important key points in this document?"
        )

with col5:

    if st.button("📝 Generate Quiz", disabled=actions_disabled):

        selected_prompt = (
            "Generate 5 quiz questions from this document."
        )

# -------------------------------
# Suggested Questions
# -------------------------------

if st.session_state.suggested_questions:

    st.subheader("💡 Suggested Questions")

    cols = st.columns(2)

    for i, q in enumerate(st.session_state.suggested_questions):

        with cols[i % 2]:

            if st.button(q, key=f"suggestion_{i}"):

                selected_prompt = q

st.divider()

# -------------------------------
# Chat Input
# -------------------------------

user_question = st.chat_input(
    "Ask a question about your document...",
    disabled=not st.session_state.uploaded
)

question = selected_prompt if selected_prompt else user_question

if question:

    st.session_state.question_count += 1

    if not st.session_state.uploaded:

        st.warning(
            "Please upload and process your PDF first."
        )

    else:

        current_time = datetime.now().strftime("%I:%M %p")

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
                "time": current_time
            }
        )

        with st.chat_message("user"):

            st.caption(f"👤 User • {current_time}")

            st.markdown(question)

        with st.spinner("🔍 Searching document..."):

            sources = retrieve_chunks(
                st.session_state.vector_store,
                question
            )

        with st.spinner("🤖 Generating answer..."):

            answer = generate_answer(
                question,
                sources,
                st.session_state.messages
            )

        assistant_time = datetime.now().strftime("%I:%M %p")

        # -------------------------------
        # Save Assistant Response
        # -------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "time": assistant_time
            }
        )

        # -------------------------------
        # Display Assistant Response
        # -------------------------------

        with st.chat_message("assistant"):

            st.caption(f"🤖 Assistant • {assistant_time}")

            placeholder = st.empty()

            streamed_text = ""

            for word in answer.split():

                streamed_text += word + " "

                placeholder.markdown(streamed_text)

                time.sleep(0.03)

            with st.expander("📚 Retrieved Sources"):

                for source in sources:

                    if isinstance(source, dict):

                        st.markdown(
                            f"**📄 {source.get('filename', 'Document')}**"
                        )

                        st.caption(
                            f"Page {source.get('page', 'Unknown')}"
                        )

                        st.write(
                            source.get("text", "")
                        )

                    else:

                        st.write(source)

                    st.divider()

# -------------------------------
# Download Chat
# -------------------------------

if st.session_state.messages:

    st.divider()

    st.subheader("💾 Export Chat")

    chat_history = ""

    for msg in st.session_state.messages:

        role = "👤 User" if msg["role"] == "user" else "🤖 Assistant"

        chat_history += f"{role}\n"
        chat_history += f"{msg['content']}\n"
        chat_history += "-" * 60 + "\n\n"

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "⬇ Download Chat (.txt)",
            data=chat_history,
            file_name="chat_history.txt",
            mime="text/plain",
            use_container_width=True
        )

        

    with col2:

        pdf_file = create_chat_pdf(
            st.session_state.messages
        )

        st.download_button(
            "📄 Download Chat (.pdf)",
            data=pdf_file,
            file_name="chat_history.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.divider()
    st.caption("Built with ❤️ using Streamlit • Google Gemini • FAISS")