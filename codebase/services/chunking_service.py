from codebase.models import Repository, SourceFile, CodeChunk
from codebase.services.code_chunker import chunk_code


def create_chunks_for_repository(repository_name):
    repository = Repository.objects.get(name=repository_name)

    source_files = SourceFile.objects.filter(repository=repository)

    total_chunks = 0

    for source_file in source_files:
        # Remove old chunks if this repository is processed again
        source_file.chunks.all().delete()

        chunks = chunk_code(source_file.content)

        for index, chunk_content in enumerate(chunks):
            CodeChunk.objects.create(
                source_file=source_file,
                content=chunk_content,
                chunk_index=index,
            )

        total_chunks += len(chunks)

    return {
        "repository": repository.name,
        "chunks_created": total_chunks,
    }