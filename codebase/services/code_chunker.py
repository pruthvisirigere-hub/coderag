from codebase.services.python_parser import extract_python_blocks


def chunk_code(content, chunk_size=80, overlap=10):
    lines = content.splitlines()

    chunks = []
    start = 0

    while start < len(lines):
        end = start + chunk_size

        chunk_lines = lines[start:end]
        chunk_content = "\n".join(chunk_lines)

        if chunk_content.strip():
            chunks.append(chunk_content)

        start += chunk_size - overlap

    return chunks


def chunk_python_code(content):
    try:
        blocks = extract_python_blocks(content)
    except SyntaxError:
        blocks = []

    if blocks:
        chunks = []

        for block in blocks:
            chunks.append(
                {
                    "content": block["content"],
                    "name": block["name"],
                    "type": block["type"],
                    "start_line": block["start_line"],
                    "end_line": block["end_line"],
                }
            )

        return chunks

    fallback_chunks = chunk_code(content)

    return [
        {
            "content": chunk,
            "name": None,
            "type": "text",
            "start_line": None,
            "end_line": None,
        }
        for chunk in fallback_chunks
    ]