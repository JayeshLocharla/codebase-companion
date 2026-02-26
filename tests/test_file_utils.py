"""Tests for app.utils.file_utils."""

from pathlib import Path

from app.utils.file_utils import collect_supported_files


def test_collect_finds_python_files(tmp_path: Path):
    (tmp_path / "a.py").write_text("x = 1\n")
    (tmp_path / "b.py").write_text("y = 2\n")

    files = collect_supported_files(str(tmp_path))
    names = [Path(f).name for f in files]
    assert "a.py" in names
    assert "b.py" in names


def test_collect_finds_yaml_files(tmp_path: Path):
    (tmp_path / "config.yaml").write_text("key: value\n")
    (tmp_path / "ci.yml").write_text("jobs:\n")

    files = collect_supported_files(str(tmp_path))
    names = [Path(f).name for f in files]
    assert "config.yaml" in names
    assert "ci.yml" in names


def test_collect_finds_markdown_files(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Title\n")
    files = collect_supported_files(str(tmp_path))
    assert any(Path(f).name == "README.md" for f in files)


def test_collect_finds_dockerfile(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")
    files = collect_supported_files(str(tmp_path))
    assert any(Path(f).name == "Dockerfile" for f in files)


def test_collect_ignores_unsupported_extensions(tmp_path: Path):
    (tmp_path / "binary.exe").write_bytes(b"\x00")
    (tmp_path / "archive.zip").write_bytes(b"\x00")
    files = collect_supported_files(str(tmp_path))
    names = [Path(f).name for f in files]
    assert "binary.exe" not in names
    assert "archive.zip" not in names


def test_collect_returns_strings(tmp_path: Path):
    (tmp_path / "x.py").write_text("")
    files = collect_supported_files(str(tmp_path))
    assert all(isinstance(f, str) for f in files)


def test_collect_empty_directory_returns_empty_list(tmp_path: Path):
    files = collect_supported_files(str(tmp_path))
    assert files == []
