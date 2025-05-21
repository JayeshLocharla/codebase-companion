import ast

def parse_python_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return []

    blocks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            code = ast.get_source_segment(source, node)
            if code:
                blocks.append({
                    "type": type(node).__name__,
                    "name": node.name,
                    "code": code,
                    "lineno": node.lineno
                })

    return blocks

if __name__ == "__main__":
    from glob import glob
    files = glob("data/repos/**/*.py", recursive=True)
    for f in files[:5]:  # Limit to 5 for preview
        print(f"\n📄 Parsing: {f}")
        parsed = parse_python_file(f)
        for block in parsed:
            print(f"- {block['type']} {block['name']} (line {block['lineno']})")
