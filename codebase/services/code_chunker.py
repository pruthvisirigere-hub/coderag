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


def chunk_markdown(content, max_lines=120):
    lines = content.splitlines()

    sections = []
    current_section = []

    for line in lines:
        # Start a new section only for top-level Markdown headings.
        if line.startswith("# ") and current_section:
            section_content = "\n".join(current_section).strip()

            if section_content:
                sections.append(section_content)

            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        section_content = "\n".join(current_section).strip()

        if section_content:
            sections.append(section_content)

    chunks = []

    for section in sections:
        section_lines = section.splitlines()

        # Keep reasonably sized Markdown sections together.
        if len(section_lines) <= max_lines:
            chunks.append(section)
            continue

        # Very large sections still need to be split.
        chunks.extend(
            chunk_code(
                section,
                chunk_size=max_lines,
                overlap=15,
            )
        )

    return chunks