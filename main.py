"""
Codebase Companion — CLI entry point.
"""

import logging
import sys

from app.config import validate_environment
from app.utils.github import download_github_repo
from app.chains.review_chain import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    print("Codebase Companion")
    try:
        validate_environment()
    except EnvironmentError as exc:
        print(f"Configuration error: {exc}")
        sys.exit(1)

    repo_url = input(
        "Enter a full GitHub repo URL (e.g. https://github.com/psf/requests): "
    ).strip()

    try:
        local_path = download_github_repo(repo_url)
        results = run_pipeline(repo_path=local_path, max_files=3)
        for section, content in results.items():
            print(f"\n{'='*60}\n{section}\n{'='*60}")
            print(content)
    except ValueError as exc:
        print(f"Invalid input: {exc}")
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error")
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
