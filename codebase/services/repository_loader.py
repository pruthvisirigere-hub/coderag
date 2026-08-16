from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
}


def load_python_files(repository_path):
    repository_path = Path(repository_path)

    source_files = []

    for file_path in repository_path.rglob("*.py"):

        if any(part in IGNORED_DIRECTORIES for part in file_path.parts):
            continue

        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        source_files.append(
            {
                "file_path": str(file_path.relative_to(repository_path)),
                "language": "python",
                "content": content,
            }
        )

    return source_files