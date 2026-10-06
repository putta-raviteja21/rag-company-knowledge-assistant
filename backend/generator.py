import os
import time

from google import genai
from google.genai.errors import ServerError


# Get Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set."
    )


# Create Gemini client
client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(question, context):
    """
    Generate an answer using the retrieved RAG context.
    """

    prompt = f"""
You are an AI Company Knowledge Assistant.

Answer the user's question using ONLY the information
provided in the context below.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If the answer cannot be found in the context, say:
  "I could not find this information in the provided company documents."
- Give a clear and concise answer.
- Use the company document information as the source of truth.

Context:
{context}

Question:
{question}

Answer:
"""

    # Retry temporary Gemini server errors
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

            return response.text

        except ServerError as error:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt

                print(
                    f"Gemini server temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                return (
                    "Gemini is temporarily unavailable. "
                    "Please try asking your question again."
                )

        except Exception as error:
            return (
                f"An error occurred while generating the answer: {error}"
            )