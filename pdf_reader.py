import os
import tempfile

from pypdf import PdfReader


def extract_text(pdf_files):

    pages = []

    for pdf in pdf_files:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf.read())
            temp_path = tmp.name

        reader = PdfReader(temp_path)

        for page_num, page in enumerate(reader.pages):
            pages.append({
                "filename": pdf.name,
                "page": page_num + 1,
                "text": page.extract_text() or ""
            })

        os.remove(temp_path)

    return pages