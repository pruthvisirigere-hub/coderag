def rerank_results(query, results):
    query_lower = query.lower()

    reranked = []

    for result in results:
        score = 0

        symbol_name = result.get("symbol_name")
        symbol_type = result.get("symbol_type")
        file_path = result.get("file_path", "").lower()

        # Exact symbol-name match
        if symbol_name and symbol_name.lower() in query_lower:
            score += 2

        # Function-related question
        if symbol_type == "FunctionDef" and "function" in query_lower:
            score += 1

        # Class-related question
        if symbol_type == "ClassDef" and "class" in query_lower:
            score += 1

        # Test-related question
        if "test" in query_lower:
            if "test" in file_path:
                score += 3

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