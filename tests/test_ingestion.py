"""Tests for app.core.ingestion."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.ingestion import ingest_repository


@pytest.fixture()
def mock_vectorstore():
    vs = MagicMock()
    vs.add_documents = MagicMock()
    return vs


def test_ingest_raises_for_missing_path():
    with pytest.raises(FileNotFoundError):
        ingest_repository("/nonexistent/path/to/repo")


def test_ingest_returns_zero_for_empty_dir(tmp_path, mock_vectorstore):
    with patch("app.core.ingestion.get_vectorstore", return_value=mock_vectorstore):
        count = ingest_repository(str(tmp_path))
    assert count == 0
    mock_vectorstore.add_documents.assert_not_called()


def test_ingest_returns_document_count(tmp_path, mock_vectorstore):
    (tmp_path / "module.py").write_text("def foo(): pass\ndef bar(): pass\n")

    with patch("app.core.ingestion.get_vectorstore", return_value=mock_vectorstore):
        count = ingest_repository(str(tmp_path))

    assert count >= 1
    mock_vectorstore.add_documents.assert_called_once()


def test_ingest_respects_max_files(tmp_path, mock_vectorstore):
    for i in range(5):
        (tmp_path / f"file{i}.py").write_text(f"def func{i}(): pass\n")

    with patch("app.core.ingestion.get_vectorstore", return_value=mock_vectorstore):
        count_limited = ingest_repository(str(tmp_path), max_files=2)

    # With 2 files, each having 1 function, we expect exactly 2 documents
    assert count_limited == 2


def test_ingest_skips_files_that_fail_to_parse(tmp_path, mock_vectorstore):
    # Write a file that will cause parse_file_by_type to raise
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("def bad syntax:\n")  # syntax error, returns []

    good_file = tmp_path / "good.py"
    good_file.write_text("def good(): pass\n")

    with patch("app.core.ingestion.get_vectorstore", return_value=mock_vectorstore):
        count = ingest_repository(str(tmp_path))

    # good.py should still be ingested
    assert count >= 1
