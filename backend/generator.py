import os
from huggingface_hub import InferenceClient


client = InferenceClient(
    api_key=os.environ["HF_TOKEN"],
    provider="auto"
)


def generate_answer(question, documents):

    if not documents:
        return (
            "I could not find the answer "
            "in the provided documents."
        )

    context = "\n\n".join(documents)

    prompt = f"""
You are a company knowledge assistant.

Answer the user's question using ONLY
the information provided in the context.

Rules:

- Do not use outside knowledge.
- Do not invent information.
- Do not guess.
- If the answer is not present in the context,
  say exactly:

"I could not find the answer in the provided documents."

- Give a short and clear answer.
- Do not show internal reasoning or thinking.

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="Qwen/Qwen3-4B-Thinking-2507",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=150
    )

    return response.choices[0].message.content