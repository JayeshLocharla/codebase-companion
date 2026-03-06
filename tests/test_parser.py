"""Tests for app.utils.parser."""

import textwrap
from pathlib import Path

import pytest

from app.utils.parser import (
    parse_python_file,
    parse_notebook_file,
    parse_text_file,
    parse_file_by_type,
)


# ── parse_python_file ──────────────────────────────────────────────────────────

def test_parse_python_file_finds_function(tmp_path: Path):
    code = "def hello(name):\n    return f'Hello, {name}'\n"
    p = tmp_path / "greet.py"
    p.write_text(code)

    blocks = parse_python_file(str(p))
    names = [b["name"] for b in blocks]
    assert "hello" in names


def test_parse_python_file_finds_class(tmp_path: Path):
    code = textwrap.dedent(
        """\
        class Foo:
            def bar(self):
                pass
        """
    )
    p = tmp_path / "foo.py"
    p.write_text(code)

    blocks = parse_python_file(str(p))
    names = [b["name"] for b in blocks]
    assert "Foo" in names
    assert "bar" in names


def test_parse_python_file_returns_empty_on_syntax_error(tmp_path: Path):
    p = tmp_path / "bad.py"
    p.write_text("def broken(:\n    pass\n")
    assert parse_python_file(str(p)) == []


def test_parse_python_file_block_has_required_keys(tmp_path: Path):
    p = tmp_path / "func.py"
    p.write_text("def f(): pass\n")
    blocks = parse_python_file(str(p))
    assert blocks
    required_keys = {"name", "type", "lineno", "code", "source", "file"}
    for block in blocks:
        assert required_keys.issubset(block.keys())


# ── parse_text_file ────────────────────────────────────────────────────────────

def test_parse_text_file_returns_single_block(tmp_path: Path):
    p = tmp_path / "README.md"
    p.write_text("# Hello\nThis is a readme.\n")

    blocks = parse_text_file(str(p), label="markdown")
    assert len(blocks) == 1
    assert blocks[0]["type"] == "markdown"
    assert "Hello" in blocks[0]["code"]


# ── parse_file_by_type ────────────────────────────────────────────────────────

def test_parse_file_by_type_routes_python(tmp_path: Path):
    p = tmp_path / "x.py"
    p.write_text("def x(): pass\n")
    blocks = parse_file_by_type(str(p))
    assert blocks
    assert all(b["source"] == "python" for b in blocks)


def test_parse_file_by_type_routes_yaml(tmp_path: Path):
    p = tmp_path / "config.yaml"
    p.write_text("key: value\n")
    blocks = parse_file_by_type(str(p))
    assert blocks
    assert blocks[0]["type"] == "yaml"


def test_parse_file_by_type_routes_markdown(tmp_path: Path):
    p = tmp_path / "notes.md"
    p.write_text("# Notes\n")
    blocks = parse_file_by_type(str(p))
    assert blocks
    assert blocks[0]["type"] == "markdown"


def test_parse_file_by_type_unknown_extension_returns_empty(tmp_path: Path):
    p = tmp_path / "binary.exe"
    p.write_bytes(b"\x00\x01\x02")
    blocks = parse_file_by_type(str(p))
    assert blocks == []
