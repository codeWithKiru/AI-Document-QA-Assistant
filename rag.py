import os

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def create_vector_store(chunks):

    documents = []

    for chunk in chunks:

        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "filename": chunk["filename"],
                    "page": chunk["page"]
                }
            )
        )

    vector_store = FAISS.from_documents(
        documents,
        embeddings
    )

    return vector_store


def retrieve_chunks(vector_store, question, k=3):

    docs = vector_store.similarity_search(
        question,
        k=k
    )

    retrieved = []

    for doc in docs:

        retrieved.append({
            "filename": doc.metadata["filename"],
            "page": doc.metadata["page"],
            "text": doc.page_content
        })

    return retrieved