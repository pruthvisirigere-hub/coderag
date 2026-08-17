def rerank_results(query, results):
    query_lower = query.lower()

    reranked = []

    for result in results:
        score = 0

        symbol_name = result.get("symbol_name")

        if symbol_name and symbol_name.lower() in query_lower:
            score += 2

        symbol_type = result.get("symbol_type")

        if symbol_type == "FunctionDef" and "function" in query_lower:
            score += 1

        if symbol_type == "ClassDef" and "class" in query_lower:
            score += 1

        reranked.append(
            {
                **result,
                "rerank_score": score,
            }
        )

    reranked.sort(
        key=lambda result: (
            -result["rerank_score"],
            result["distance"],
        )
    )

    return reranked