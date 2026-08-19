from codebase.models import Repository, CodeChunk
from codebase.services.code_chunker import (
    chunk_code,
    chunk_markdown,
    chunk_python_code,
)


def create_chunks_for_repository(repository_name):
    repository = Repository.objects.get(
        name=repository_name
    )

    source_files = repository.source_files.all()

    total_chunks = 0

    for source_file in source_files:
        source_file.chunks.all().delete()

        if source_file.language == "python":
            chunks = chunk_python_code(
                source_file.content
            )

            for index, chunk in enumerate(chunks):
                CodeChunk.objects.create(
                    source_file=source_file,
                    content=chunk["content"],
                    chunk_index=index,
                    symbol_name=chunk["name"],
                    symbol_type=chunk["type"],
                    start_line=chunk["start_line"],
                    end_line=chunk["end_line"],
                )

        elif source_file.language == "markdown":
            chunks = chunk_markdown(
                source_file.content
            )

            for index, chunk_content in enumerate(chunks):
                CodeChunk.objects.create(
                    source_file=source_file,
                    content=chunk_content,
                    chunk_index=index,
                    symbol_type="markdown_section",
                )

        else:
            chunks = chunk_code(
                source_file.content
            )

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