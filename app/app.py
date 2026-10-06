import sys
import os
import json
from datetime import datetime


sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


import streamlit as st


from backend.document_loader import (
    extract_pages_from_pdf
)

from backend.chunker import (
    split_pages_into_chunks
)

from backend.embeddings import (
    create_embeddings
)

from backend.vector_store import (
    store_chunks
)

from backend.retriever import (
    retrieve_documents
)

from backend.generator import (
    generate_answer
)

from backend.document_id import (
    create_document_id
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

HISTORY_FILE = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "history",
    "chat_history.json"
)


# --------------------------------------------------
# History functions
# --------------------------------------------------

def load_history():

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_history(history):

    os.makedirs(
        os.path.dirname(HISTORY_FILE),
        exist_ok=True
    )

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="RAG Company Assistant",
    page_icon="📚",
    layout="wide"
)


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title(
    "📚 RAG Company Knowledge Assistant"
)

st.write(
    "Upload company documents and ask questions "
    "using AI-powered semantic search."
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("Project Information")

    st.write(
        "LLM: Gemini 3.8 Flash"
    )

    st.write(
        "Embeddings: all-MiniLM-L6-v2"
    )

    st.write(
        "Vector DB: ChromaDB"
    )

    st.write(
        "Framework: Streamlit"
    )

    st.divider()

    st.header("Chat History")

    history = load_history()

    st.write(
        f"Saved conversations: {len(history)}"
    )


    if st.button(
        "Clear Chat History"
    ):

        save_history([])

        st.success(
            "Chat history cleared."
        )

        st.rerun()


# --------------------------------------------------
# Upload documents
# --------------------------------------------------

st.subheader(
    "1. Upload Company Documents"
)


uploaded_files = st.file_uploader(

    "Select one or more PDF files",

    type=["pdf"],

    accept_multiple_files=True
)


if uploaded_files:

    st.write(
        "Selected documents:"
    )

    for uploaded_file in uploaded_files:

        st.write(
            f"📄 {uploaded_file.name}"
        )


    # --------------------------------------------------
    # Process documents
    # --------------------------------------------------

    if st.button(
        "Process Documents"
    ):

        total_characters = 0

        total_pages = 0

        total_chunks = 0

        processed_documents = 0

        skipped_documents = 0


        progress = st.progress(0)


        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            try:

                st.write(
                    f"Processing: "
                    f"{uploaded_file.name}"
                )


                # Read file
                file_bytes = (
                    uploaded_file.getvalue()
                )


                # Create unique document ID
                document_id = (
                    create_document_id(
                        file_bytes
                    )
                )


                # Extract PDF pages
                pages = (
                    extract_pages_from_pdf(
                        uploaded_file
                    )
                )


                if not pages:

                    st.warning(
                        f"{uploaded_file.name} "
                        "contains no readable text."
                    )

                    skipped_documents += 1

                    continue


                # Statistics
                total_characters += sum(
                    len(page["text"])
                    for page in pages
                )

                total_pages += len(pages)


                # Source filename
                source_name = (
                    uploaded_file.name
                )


                # Create chunks
                chunks = (
                    split_pages_into_chunks(
                        pages,
                        source_name,
                        document_id
                    )
                )


                # Create embeddings
                embeddings = (
                    create_embeddings(
                        chunks
                    )
                )


                # Store in ChromaDB
                stored_count = (
                    store_chunks(
                        chunks,
                        embeddings
                    )
                )


                if stored_count == 0:

                    st.warning(
                        f"{uploaded_file.name} "
                        "was already processed."
                    )

                    skipped_documents += 1

                else:

                    total_chunks += (
                        stored_count
                    )

                    processed_documents += 1


            except Exception as e:

                st.error(
                    f"Error processing "
                    f"{uploaded_file.name}: {e}"
                )


            progress.progress(
                (index + 1)
                / len(uploaded_files)
            )


        st.success(
            "Document processing completed!"
        )


        st.write(
            f"New documents processed: "
            f"{processed_documents}"
        )

        st.write(
            f"Documents skipped: "
            f"{skipped_documents}"
        )

        st.write(
            f"Total characters: "
            f"{total_characters}"
        )

        st.write(
            f"Total pages: "
            f"{total_pages}"
        )

        st.write(
            f"New chunks stored: "
            f"{total_chunks}"
        )


# --------------------------------------------------
# Question section
# --------------------------------------------------

st.divider()

st.subheader(
    "2. Ask a Question"
)


question = st.text_input(
    "Enter your question"
)


if question:

    with st.spinner(
        "Searching documents..."
    ):

        results = retrieve_documents(
            question
        )


    if not results:

        answer = (
            "I could not find the answer "
            "in the provided documents."
        )

        st.warning(answer)

    else:

        with st.spinner(
            "Gemini is generating the answer..."
        ):

            answer = generate_answer(

                question,

                [
                    item["text"]
                    for item in results
                ]
            )


        # --------------------------------------------------
        # Display answer
        # --------------------------------------------------

        st.subheader(
            "Answer"
        )

        st.write(answer)


        # --------------------------------------------------
        # Display sources
        # --------------------------------------------------

        st.subheader(
            "Sources"
        )


        for i, item in enumerate(
            results
        ):

            with st.expander(

                f"📄 {item['source']} "
                f"— Page {item['page']}"

            ):

                st.write(
                    f"Retrieval distance: "
                    f"{item['distance']:.3f}"
                )

                st.text(
                    item["text"]
                )


        # --------------------------------------------------
        # Save chat history
        # --------------------------------------------------

        history = load_history()


        history_entry = {

            "timestamp": (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            ),

            "question": question,

            "answer": answer,

            "sources": [

                {
                    "source": item["source"],

                    "page": item["page"]
                }

                for item in results

            ]

        }


        history.append(
            history_entry
        )


        save_history(
            history
        )


# --------------------------------------------------
# Previous conversations
# --------------------------------------------------

st.divider()

st.subheader(
    "3. Previous Questions"
)


history = load_history()


if history:

    for index, item in enumerate(
        reversed(history)
    ):

        with st.expander(

            f"Question {len(history) - index}: "
            f"{item['question']}"

        ):

            st.write(
                f"🕒 {item['timestamp']}"
            )

            st.markdown(
                "**Answer:**"
            )

            st.write(
                item["answer"]
            )

            st.markdown(
                "**Sources:**"
            )

            for source in item["sources"]:

                st.write(
                    f"📄 {source['source']} "
                    f"— Page {source['page']}"
                )

else:

    st.info(
        "No previous questions yet."
    )