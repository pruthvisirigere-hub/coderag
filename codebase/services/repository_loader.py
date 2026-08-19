from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
}


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".md": "markdown",
}


def load_repository_files(repository_path):
    repository_path = Path(repository_path)

    source_files = []

    for file_path in repository_path.rglob("*"):
        if not file_path.is_file():
            continue

        if any(
            part in IGNORED_DIRECTORIES
            for part in file_path.parts
        ):
            continue

        language = SUPPORTED_EXTENSIONS.get(
            file_path.suffix.lower()
        )

        if language is None:
            continue

        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        source_files.append(
            {
                "file_path": str(
                    file_path.relative_to(repository_path)
                ),
                "language": language,
                "content": content,
            }
        )

    return source_files