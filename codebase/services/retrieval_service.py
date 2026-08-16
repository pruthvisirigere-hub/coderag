from pgvector.django import CosineDistance

from codebase.models import CodeChunk
from codebase.services.embedding_service import generate_embedding


def search_similar_code(query, repository_name, limit=5):
    query_embedding = generate_embedding(query)

    chunks = (
        CodeChunk.objects
        .filter(
            source_file__repository__name=repository_name,
            embedding__isnull=False,
        )
        .annotate(
            distance=CosineDistance("embedding", query_embedding)
        )
        .order_by("distance")[:limit]
    )

    results = []

    for chunk in chunks:
        results.append(
            {
                "file_path": chunk.source_file.file_path,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "distance": chunk.distance,
            }
        )

    return results