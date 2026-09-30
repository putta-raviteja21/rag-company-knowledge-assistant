from sentence_transformers import SentenceTransformer
import chromadb


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


client = chromadb.PersistentClient(
    path="chroma_db"
)


collection = client.get_collection(
    name="company_documents"
)


def retrieve_documents(
    question,
    number_of_results=3,
    max_distance=1.0
):

    question_embedding = model.encode(
        [question]
    )[0]


    results = collection.query(

        query_embeddings=[
            question_embedding.tolist()
        ],

        n_results=number_of_results,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]


    retrieved_results = []


    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        if distance <= max_distance:

            retrieved_results.append({

                "text": document,

                "page": metadata["page"],

                "source": metadata["source"],

                "distance": distance
            })


    return retrieved_results