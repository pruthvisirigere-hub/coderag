import os

from openai import OpenAI


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

def generate_answer(prompt):
    model = os.getenv("OPENROUTER_MODEL")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a codebase assistant. "
                    "Answer questions using only the provided repository context. "
                    "If the context does not contain enough information, say so."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content