from pathlib import Path

def collect_supported_files(code_dir: str) -> list:
    """Collect all supported source files from the code directory."""
    file_types = [".py", ".ipynb", ".md", ".yaml", ".yml"]
    all_files = []

    for ext in file_types:
        all_files.extend(Path(code_dir).rglob(f"*{ext}"))

    # Explicitly include Dockerfile
    all_files.extend(Path(code_dir).rglob("Dockerfile"))

    return [str(f) for f in all_files]
