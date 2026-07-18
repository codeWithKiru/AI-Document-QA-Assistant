from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(pages):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = []

    for page in pages:

        split_chunks = splitter.split_text(page["text"])

        for chunk in split_chunks:

            chunks.append({
                "filename": page["filename"],
                "page": page["page"],
                "text": chunk
            })

    return chunks