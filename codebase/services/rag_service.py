from codebase.services.retrieval_service import search_similar_code
from codebase.services.llm_service import generate_answer

def build_rag_context(question, repository_name, limit=5):
    results = search_similar_code(
        query=question,
        repository_name=repository_name,
        limit=limit,
    )

    context_parts = []

    for result in results:
        context_parts.append(
            f"""
        File: {result["file_path"]}
        Symbol: {result["symbol_name"]}
        Type: {result["symbol_type"]}
        Lines: {result["start_line"]} - {result["end_line"]}
        Chunk: {result["chunk_index"]}

        Code:
        {result["content"]}
        """
        )

    return "\n".join(context_parts)

def answer_codebase_question(question, repository_name):
    context = build_rag_context(
        question=question,
        repository_name=repository_name,
    )

    prompt = f"""
    You are answering a question about a software codebase.

    Use ONLY the repository context provided below.

    Question:
    {question}

    Repository Context:
    {context}

    Instructions:
    - Answer the question clearly.
    - Base the answer only on the retrieved repository context.
    - When start and end line numbers are available, mention them in the answer.
    - Mention the exact file path(s) where the relevant code was found.
    - Do not invent files or functionality.
    - If the context is insufficient, clearly say that you do not have enough information.

    At the end, include:

    Sources:
    - <file path>
    """

    return generate_answer(prompt)