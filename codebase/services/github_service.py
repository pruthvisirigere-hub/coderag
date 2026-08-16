import shutil
import tempfile
from pathlib import Path

from git import Repo

from codebase.models import Repository
from codebase.services.chunking_service import create_chunks_for_repository
from codebase.services.embedding_service import generate_embeddings_for_chunks
from codebase.services.ingestion_service import ingest_local_repository


def clone_github_repository(github_url):
    temp_dir = tempfile.mkdtemp()

    Repo.clone_from(
        github_url,
        temp_dir,
    )

    return Path(temp_dir)


def ingest_github_repository(name, github_url):
    temp_path = clone_github_repository(github_url)

    try:
        ingestion_result = ingest_local_repository(
            name=name,
            repository_path=str(temp_path),
        )

        repository = Repository.objects.get(name=name)
        repository.github_url = github_url
        repository.local_path = None
        repository.save(
            update_fields=["github_url", "local_path"]
        )

        chunk_result = create_chunks_for_repository(name)

        embeddings_created = generate_embeddings_for_chunks()

        return {
            "repository": name,
            "files_processed": ingestion_result["files_processed"],
            "chunks_created": chunk_result["chunks_created"],
            "embeddings_created": embeddings_created,
        }

    finally:
        shutil.rmtree(temp_path, ignore_errors=True)