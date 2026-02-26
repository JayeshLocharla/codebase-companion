"""Shared pytest fixtures for Codebase Companion tests."""

import os
import textwrap
from pathlib import Path

import pytest


@pytest.fixture()
def tmp_python_file(tmp_path: Path) -> Path:
    """Write a small Python file with a function and class into a temp dir."""
    code = textwrap.dedent(
        """\
        def add(a, b):
            return a + b

        class Calculator:
            def multiply(self, x, y):
                return x * y
        """
    )
    p = tmp_path / "sample.py"
    p.write_text(code)
    return p


@pytest.fixture()
def tmp_repo_dir(tmp_path: Path, tmp_python_file: Path) -> Path:
    """Return a temp directory that mimics a cloned repository."""
    return tmp_path


@pytest.fixture(autouse=True)
def no_real_openai(monkeypatch):
    """
    Prevent any test from accidentally calling the real OpenAI API.
    If OPENAI_API_KEY is not already set, inject a fake key so that
    ChatOpenAI instantiation does not raise a missing-key error.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key-for-unit-tests")
