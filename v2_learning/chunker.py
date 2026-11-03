import ast
import sys

from mini_loader import load_files  # Piece 1: finds and reads the files

PYTHON_BLOCK_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


# ---------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------
def make_chunk(text, name, kind, start_line, end_line):
    """Every chunk in v2 has exactly these five things."""
    return {
        "content": text,
        "name": name,
        "type": kind,
        "start_line": start_line,
        "end_line": end_line,
    }


def trim_blank_edges(lines, start, end):
    """Move start/end inward so the range does not begin or end on a blank line.
    Line numbers start at 1. Returns None if nothing but blanks is left."""
    while start <= end and not lines[start - 1].strip():
        start += 1
    while end >= start and not lines[end - 1].strip():
        end -= 1
    if start > end:
        return None
    return start, end


# ---------------------------------------------------------------
# Rule 3: fixed windows (used for "other" files and broken Python)
# ---------------------------------------------------------------
def chunk_windows(lines, first_line=1, size=80, overlap=10, name=None, kind="text"):
    chunks = []
    total = len(lines)
    start = 0

    while start < total:
        end = min(start + size, total)
        text = "\n".join(lines[start:end])

        if text.strip():
            chunks.append(
                make_chunk(text, name, kind, first_line + start, first_line + end - 1)
            )

        if end >= total:  # we reached the end, so stop (no tiny leftover chunk)
            break

        start += size - overlap  # next window starts a bit before this one ended

    return chunks


# ---------------------------------------------------------------
# Rule 1: Python files
# ---------------------------------------------------------------
def chunk_python(content):
    lines = content.splitlines()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return chunk_windows(lines)  # cannot parse, so fall back to windows

    chunks = []
    covered = set()  # line numbers already inside a function or class

    for node in tree.body:
        if isinstance(node, PYTHON_BLOCK_TYPES):
            # a decorator such as @app.route sits ABOVE the def line, so include it
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            end = node.end_lineno

            covered.update(range(start, end + 1))
            text = "\n".join(lines[start - 1:end])
            chunks.append(make_chunk(text, node.name, type(node).__name__, start, end))

    # Everything NOT covered (imports, constants, top-level code) is grouped into
    # stretches of consecutive lines. Each stretch becomes a "module code" chunk.
    run_start = None
    for number in range(1, len(lines) + 2):  # +2 so the last stretch gets closed
        is_leftover = number <= len(lines) and number not in covered

        if is_leftover and run_start is None:
            run_start = number
        elif not is_leftover and run_start is not None:
            span = trim_blank_edges(lines, run_start, number - 1)
            if span:
                s, e = span
                text = "\n".join(lines[s - 1:e])
                chunks.append(make_chunk(text, "module_level_code", "ModuleCode", s, e))
            run_start = None

    chunks.sort(key=lambda c: c["start_line"])  # keep file order
    return chunks


# ---------------------------------------------------------------
# Rule 2: Markdown files
# ---------------------------------------------------------------
def chunk_markdown(content, max_lines=120):
    lines = content.splitlines()

    # 1. find the headings, ignoring "# " lines that sit inside ``` code blocks
    headings = []  # (line number, title)
    inside_code_block = False

    for number, line in enumerate(lines, start=1):
        if line.lstrip().startswith(("```", "~~~")):
            inside_code_block = not inside_code_block
            continue
        if not inside_code_block and line.startswith("# "):
            headings.append((number, line[2:].strip()))

    # 2. turn headings into sections: (first line, last line, title)
    sections = []
    starts = [number for number, _ in headings]

    if not starts:
        sections.append((1, len(lines), None))
    elif starts[0] > 1:
        sections.append((1, starts[0] - 1, None))  # text before the first heading

    for i, (number, title) in enumerate(headings):
        last = starts[i + 1] - 1 if i + 1 < len(starts) else len(lines)
        sections.append((number, last, title))

    # 3. one chunk per section; a very long section is cut into windows
    chunks = []
    for first, last, title in sections:
        span = trim_blank_edges(lines, first, last)
        if span is None:
            continue
        s, e = span

        if e - s + 1 <= max_lines:
            text = "\n".join(lines[s - 1:e])
            chunks.append(make_chunk(text, title, "markdown_section", s, e))
        else:
            chunks.extend(
                chunk_windows(
                    lines[s - 1:e], first_line=s, size=max_lines, overlap=15,
                    name=title, kind="markdown_section",
                )
            )

    return chunks


# ---------------------------------------------------------------
# Choose the rule for a file
# ---------------------------------------------------------------
def chunk_file(source_file):
    language = source_file["language"]
    content = source_file["content"]

    if language == "python":
        chunks = chunk_python(content)
    elif language == "markdown":
        chunks = chunk_markdown(content)
    else:
        chunks = chunk_windows(content.splitlines())

    for chunk in chunks:
        chunk["file_path"] = source_file["file_path"]
    return chunks


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage: python chunker.py <folder> [file to inspect]")
        sys.exit(1)

    files, _ = load_files(sys.argv[1])
    inspect = sys.argv[2] if len(sys.argv) == 3 else None

    total = 0
    missing_lines = 0
    found = False

    for f in files:
        chunks = chunk_file(f)
        total += len(chunks)
        missing_lines += sum(
            1 for c in chunks if c["start_line"] is None or c["end_line"] is None
        )

        if inspect is None:
            print(f"{len(chunks):>3} chunks  {f['language']:<10} {f['file_path']}")
        elif f["file_path"] == inspect:
            found = True
            print(f"Chunks in {inspect}:")
            for c in chunks:
                print(
                    f"  {c['type']:<16} {str(c['name']):<28} "
                    f"lines {c['start_line']}-{c['end_line']}"
                )

    if inspect is not None and not found:
        print(f"File not found in the scan: {inspect}")

    print()
    print(f"Files: {len(files)}   Chunks: {total}   Chunks missing line numbers: {missing_lines}")
