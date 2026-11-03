import sys
from pathlib import Path

# Folders we never want to look inside
IGNORED_DIRECTORIES = {".git", ".venv", "venv", "__pycache__"}

# File types we keep, chosen by the ending of the file name
SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".md": "markdown",
    ".txt": "text",
    ".yml": "yaml",
    ".yaml": "yaml",
}

# Files with no ending, chosen by their exact name
SUPPORTED_FILENAMES = {
    "Dockerfile": "dockerfile",
}

# Files bigger than this are skipped (200,000 bytes is about 200 KB)
MAX_FILE_SIZE_BYTES = 200_000


def load_files(folder):
    folder = Path(folder)
    kept = []
    too_large = []

    for file_path in folder.rglob("*"):
        # 1. skip anything that is not a file (folders)
        if not file_path.is_file():
            continue

        # 2. skip files that live inside an ignored folder
        relative_parts = file_path.relative_to(folder).parts
        if any(part in IGNORED_DIRECTORIES for part in relative_parts):
            continue

        # 3. keep only supported types: check the exact name first,
        #    then the ending of the name
        language = SUPPORTED_FILENAMES.get(file_path.name)
        if language is None:
            language = SUPPORTED_EXTENSIONS.get(file_path.suffix.lower())
        if language is None:
            continue

        # 4. skip files that are too big
        size = file_path.stat().st_size
        if size > MAX_FILE_SIZE_BYTES:
            too_large.append((str(file_path.relative_to(folder)), size))
            continue

        # 5. read the text inside the file
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        kept.append(
            {
                "file_path": str(file_path.relative_to(folder)),
                "language": language,
                "content": content,
            }
        )

    return kept, too_large


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mini_loader.py <folder>")
        sys.exit(1)

    files, too_large = load_files(sys.argv[1])

    for f in files:
        print(f"{f['language']:<10} {len(f['content']):>7} chars  {f['file_path']}")

    if too_large:
        print()
        print("Skipped because too large:")
        for path, size in too_large:
            print(f"  {path} ({size:,} bytes)")

    print()
    print(f"Total files kept: {len(files)}")
    print(f"Total files skipped for size: {len(too_large)}")
