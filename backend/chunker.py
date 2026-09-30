def split_pages_into_chunks(
    pages,
    source_name,
    document_id,
    chunk_size=500,
    overlap=50
):

    chunks = []

    for page in pages:

        page_number = page["page"]
        text = page["text"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "page": page_number,
                "source": source_name,
                "document_id": document_id
            })

            start = end - overlap

    return chunks