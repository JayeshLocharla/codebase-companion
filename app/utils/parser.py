import os
import ast
import nbformat

def parse_python_file(filepath):
    """Parse .py files using AST to extract function and class blocks."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    blocks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            code = ast.get_source_segment(source, node)
            blocks.append({
                "name": node.name,
                "type": type(node).__name__,
                "lineno": node.lineno,
                "code": code,
                "source": "python",
                "file": filepath
            })
    return blocks


def parse_notebook_file(filepath):
    """Parse Jupyter notebooks and extract code cells."""
    with open(filepath, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    blocks = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            blocks.append({
                "name": f"cell_{i}",
                "type": "CodeCell",
                "lineno": i,
                "code": cell.source,
                "source": "notebook",
                "file": filepath
            })
    return blocks


def parse_text_file(filepath, label="text"):
    """Generic text file parser for markdown, yaml, Dockerfile, etc."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return [{
        "name": os.path.basename(filepath),
        "type": label,
        "lineno": 0,
        "code": content,
        "source": label,
        "file": filepath
    }]


def parse_file_by_type(filepath):
    """Auto-detect file type and route to the appropriate parser."""
    ext = os.path.splitext(filepath)[-1].lower()
    filename = os.path.basename(filepath).lower()

    if ext == ".py":
        return parse_python_file(filepath)
    elif ext == ".ipynb":
        return parse_notebook_file(filepath)
    elif ext in [".yml", ".yaml"]:
        return parse_text_file(filepath, label="yaml")
    elif ext == ".md":
        return parse_text_file(filepath, label="markdown")
    elif filename == "dockerfile":
        return parse_text_file(filepath, label="docker")
    else:
        return []


if __name__ == "__main__":
    import sys

    print("🔍 Testing parser module...\n")

    # Example: Provide file path as CLI arg
    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_file>")
        sys.exit(1)

    test_file = sys.argv[1]
    if not os.path.exists(test_file):
        print(f"❌ File not found: {test_file}")
        sys.exit(1)

    blocks = parse_file_by_type(test_file)
    print(f"✅ Parsed {len(blocks)} blocks from: {test_file}\n")

    for block in blocks:
        print(f"📄 {block['type']} - {block['name']} ({block['source']})")
        print("-" * 40)
        print(block["code"][:500])  # preview only first 500 chars
        print("=" * 80)
