"""
GitHub repository cloning utility.

Security hardening vs original:
- Validates URL scheme is ``https`` only (prevents file://, git://, ssh:// abuse).
- Validates hostname is ``github.com`` only (prevents SSRF to internal hosts).
- Raises descriptive exceptions instead of broad ``except Exception``.
"""

import logging
import subprocess
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_ALLOWED_SCHEMES = {"https"}
_ALLOWED_HOSTS = {"github.com"}


def download_github_repo(repo_url: str, target_dir: str = "data/repos") -> str:
    """
    Clone a GitHub repository and return the local path.

    The repository is only cloned once; subsequent calls with the same URL
    return the cached path immediately.

    Args:
        repo_url:   Full HTTPS GitHub URL, e.g. ``https://github.com/owner/repo``.
        target_dir: Directory under which repos are stored.

    Returns:
        Absolute path to the cloned repository.

    Raises:
        ValueError: If ``repo_url`` is not a valid HTTPS GitHub URL.
        subprocess.CalledProcessError: If ``git clone`` fails.
    """
    _validate_github_url(repo_url)

    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")
    owner, repo_name = parts[0], parts[1]

    Path(target_dir).mkdir(parents=True, exist_ok=True)
    local_path = Path(target_dir) / f"{owner}_{repo_name}"

    if local_path.exists():
        logger.info("Repo already cached at %s", local_path)
        return str(local_path)

    logger.info("Cloning %s -> %s", repo_url, local_path)
    subprocess.run(
        ["git", "clone", repo_url, str(local_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    logger.info("Clone complete: %s", local_path)
    return str(local_path)


def _validate_github_url(url: str) -> None:
    """
    Validate that ``url`` is a safe GitHub HTTPS URL.

    Args:
        url: The URL to validate.

    Raises:
        ValueError: If the URL is not a valid HTTPS GitHub repository URL.
    """
    try:
        parsed = urlparse(url)
    except Exception as exc:
        raise ValueError(f"Could not parse URL: {url!r}") from exc

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError(
            f"Unsafe URL scheme {parsed.scheme!r}. Only HTTPS GitHub URLs are allowed."
        )

    if parsed.hostname not in _ALLOWED_HOSTS:
        raise ValueError(
            f"Host {parsed.hostname!r} is not allowed. Only github.com URLs are accepted."
        )

    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(
            "Invalid GitHub URL. Expected format: https://github.com/owner/repo"
        )
