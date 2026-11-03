import sys
from pathlib import Path

# Folders we never want to look inside
IGNORED_DIRECTORIES = {".git", ".venv", "venv", "__pycache__"}

# Only these file types are kept, and the label we give each
SUPPORTED_EXTENSIONS = {".py": "python", ".md": "markdown"}


def load_files(folder):
    folder = Path(folder)
    kept = []

    for file_path in folder.rglob("*"):
        # 1. skip anything that is not a file (folders)
        if not file_path.is_file():
            continue

        # 2. skip files that live inside an ignored folder
        relative_parts = file_path.relative_to(folder).parts
        if any(part in IGNORED_DIRECTORIES for part in relative_parts):
            continue

        # 3. keep only .py and .md
        language = SUPPORTED_EXTENSIONS.get(file_path.suffix.lower())
        if language is None:
            continue

        # 4. read the text inside the file
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        kept.append(
            {
                "file_path": str(file_path.relative_to(folder)),
                "language": language,
                "content": content,
            }
        )

    return kept


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mini_loader.py <folder>")
        sys.exit(1)

    files = load_files(sys.argv[1])

    for f in files:
        print(f"{f['language']:<9} {len(f['content']):>6} chars  {f['file_path']}")

    print()
    print(f"Total files kept: {len(files)}")
