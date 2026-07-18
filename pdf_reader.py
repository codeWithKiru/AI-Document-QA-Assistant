import os
import tempfile

from langchain_community.document_loaders import PyPDFLoader


def extract_text(pdf_files):

    pages = []

    for pdf in pdf_files:

        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

            tmp.write(pdf.read())

            temp_path = tmp.name

        # Load PDF using LangChain
        loader = PyPDFLoader(temp_path)

        documents = loader.load()

        for doc in documents:

            pages.append({
                "filename": pdf.name,
                "page": doc.metadata.get("page", 0) + 1,
                "text": doc.page_content
            })

        # Delete temporary file
        os.remove(temp_path)

    return pages