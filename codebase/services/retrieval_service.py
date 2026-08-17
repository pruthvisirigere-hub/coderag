from pgvector.django import CosineDistance

from codebase.models import CodeChunk
from codebase.services.embedding_service import generate_embedding
from codebase.services.reranking_service import rerank_results


def search_similar_code(query, repository_name, limit=5):
    query_embedding = generate_embedding(query)

    # Retrieve more candidates first so the reranker has options.
    candidate_limit = limit * 3

    chunks = (
        CodeChunk.objects
        .filter(
            source_file__repository__name=repository_name,
            embedding__isnull=False,
        )
        .annotate(
            distance=CosineDistance("embedding", query_embedding)
        )
        .order_by("distance")[:candidate_limit]
    )

    results = []

    for chunk in chunks:
        results.append(
            {
                "file_path": chunk.source_file.file_path,
                "chunk_index": chunk.chunk_index,
                "symbol_name": chunk.symbol_name,
                "symbol_type": chunk.symbol_type,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "content": chunk.content,
                "distance": chunk.distance,
            }
        )

    reranked_results = rerank_results(query, results)

    return reranked_results[:limit]