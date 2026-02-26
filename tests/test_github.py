"""Tests for app.utils.github — URL validation and cloning logic."""

import pytest
from unittest.mock import patch, MagicMock

from app.utils.github import _validate_github_url, download_github_repo


# ── _validate_github_url ──────────────────────────────────────────────────────

def test_valid_github_url_passes():
    _validate_github_url("https://github.com/psf/requests")


def test_valid_github_url_with_trailing_slash_passes():
    _validate_github_url("https://github.com/psf/requests/")


def test_http_scheme_raises():
    with pytest.raises(ValueError, match="scheme"):
        _validate_github_url("http://github.com/user/repo")


def test_file_scheme_raises():
    with pytest.raises(ValueError, match="scheme"):
        _validate_github_url("file:///etc/passwd")


def test_non_github_host_raises():
    with pytest.raises(ValueError, match="Host"):
        _validate_github_url("https://gitlab.com/user/repo")


def test_internal_host_raises():
    with pytest.raises(ValueError, match="Host"):
        _validate_github_url("https://internal.company.com/user/repo")


def test_missing_repo_name_raises():
    with pytest.raises(ValueError):
        _validate_github_url("https://github.com/onlyowner")


def test_empty_url_raises():
    with pytest.raises(ValueError):
        _validate_github_url("")


# ── download_github_repo ──────────────────────────────────────────────────────

def test_download_skips_clone_if_already_exists(tmp_path):
    # Create a fake local repo directory
    fake_repo = tmp_path / "psf_requests"
    fake_repo.mkdir()

    result = download_github_repo(
        "https://github.com/psf/requests",
        target_dir=str(tmp_path),
    )
    assert result == str(fake_repo)


def test_download_calls_git_clone(tmp_path):
    with patch("app.utils.github.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = download_github_repo(
            "https://github.com/psf/requests",
            target_dir=str(tmp_path),
        )
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "git"
        assert call_args[1] == "clone"


def test_download_raises_on_invalid_url(tmp_path):
    with pytest.raises(ValueError):
        download_github_repo("http://evil.com/user/repo", target_dir=str(tmp_path))
