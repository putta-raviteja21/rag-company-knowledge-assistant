import chromadb


client = chromadb.PersistentClient(
    path="chroma_db"
)


collection = client.get_or_create_collection(
    name="company_documents"
)


def document_exists(document_id):

    results = collection.get(
        where={
            "document_id": document_id
        },
        limit=1
    )

    return len(results["ids"]) > 0


def store_chunks(chunks, embeddings):

    if not chunks:

        return 0


    document_id = chunks[0]["document_id"]


    if document_exists(document_id):

        return 0


    ids = []
    documents = []
    metadatas = []


    for i, chunk in enumerate(chunks):

        source_name = chunk["source"]

        safe_source_name = source_name.replace(
            " ",
            "_"
        )

        chunk_id = (
            f"{document_id}_"
            f"{safe_source_name}_"
            f"chunk_{i}"
        )

        ids.append(chunk_id)

        documents.append(
            chunk["text"]
        )

        metadatas.append({

            "page": chunk["page"],

            "source": chunk["source"],

            "document_id": chunk["document_id"]
        })


    collection.add(

        ids=ids,

        documents=documents,

        embeddings=embeddings.tolist(),

        metadatas=metadatas
    )


    return len(chunks)