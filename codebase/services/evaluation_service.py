from codebase.services.retrieval_service import search_similar_code


def evaluate_retrieval(
    repository_name,
    question,
    expected_file,
    limit=5,
):
    results = search_similar_code(
        query=question,
        repository_name=repository_name,
        limit=limit,
    )

    retrieved_files = [
        result["file_path"].replace("\\", "/")
        for result in results
    ]

    expected_file = expected_file.replace("\\", "/")

    found = expected_file in retrieved_files

    rank = None

    if found:
        rank = retrieved_files.index(expected_file) + 1

    return {
        "question": question,
        "expected_file": expected_file,
        "retrieved_files": retrieved_files,
        "found": found,
        "rank": rank,
    }

def evaluate_multiple_cases(cases):
    results = []

    for case in cases:
        result = evaluate_retrieval(
            repository_name=case["repository"],
            question=case["question"],
            expected_file=case["expected_file"],
        )

        results.append(result)

    return results

def calculate_evaluation_metrics(results):
    total_cases = len(results)

    if total_cases == 0:
        return {
            "total_cases": 0,
            "top_1_accuracy": 0,
            "top_5_accuracy": 0,
        }

    top_1_correct = sum(
        1 for result in results
        if result["rank"] == 1
    )

    top_5_correct = sum(
        1 for result in results
        if result["found"]
    )

    return {
        "total_cases": total_cases,
        "top_1_correct": top_1_correct,
        "top_5_correct": top_5_correct,
        "top_1_accuracy": top_1_correct / total_cases,
        "top_5_accuracy": top_5_correct / total_cases,
    }