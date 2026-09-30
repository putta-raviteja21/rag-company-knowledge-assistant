import ollama


def generate_answer(question, documents):

    if not documents:

        return (
            "I could not find the answer "
            "in the provided documents."
        )


    context = "\n\n".join(
        documents
    )


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


    response = ollama.chat(

        model="qwen3:4b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        think=False,

        options={
            "temperature": 0.1,
            "num_predict": 150
        }
    )


    return response.message.content