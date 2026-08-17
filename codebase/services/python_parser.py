import ast


def extract_python_blocks(content):
    tree = ast.parse(content)

    blocks = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1
            end_line = node.end_lineno

            lines = content.splitlines()
            block_content = "\n".join(lines[start_line:end_line])

            blocks.append(
                {
                    "name": node.name,
                    "type": node.__class__.__name__,
                    "content": block_content,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                }
            )

    return blocks