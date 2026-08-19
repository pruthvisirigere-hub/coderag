from codebase.models import Repository, SourceFile
from codebase.services.repository_loader import (
    load_repository_files,
)


def ingest_local_repository(name, repository_path):
    repository, _ = Repository.objects.get_or_create(
        name=name,
        defaults={
            "local_path": repository_path,
        },
    )

    files = load_repository_files(repository_path)

    for file_data in files:
        SourceFile.objects.update_or_create(
            repository=repository,
            file_path=file_data["file_path"],
            defaults={
                "language": file_data["language"],
                "content": file_data["content"],
            },
        )

    return {
        "repository": repository.name,
        "files_processed": len(files),
    }