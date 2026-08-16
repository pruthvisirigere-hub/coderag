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