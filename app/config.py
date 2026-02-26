"""
Central configuration for Codebase Companion.

All tunable parameters are defined here and read from environment variables
with sensible defaults. No agent or utility should hardcode these values.
"""

import os
import logging
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Config:
    # LLM settings
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature_analysis: float = 0.2   # lower = more deterministic
    openai_temperature_generation: float = 0.3  # slightly more creative for docs/tests

    # Embedding model
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Vector store
    chroma_persist_directory: str = "chroma_db"
    retriever_k: int = 4  # number of retrieved code chunks for Analyzer

    # Data directories
    default_repos_dir: str = "data/repos"

    # Pipeline defaults
    default_max_files: int = 3
    default_max_blocks: int = 50

    @classmethod
    def from_env(cls) -> "Config":
        """Build Config from environment variables, falling back to defaults."""
        return cls(
            openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            chroma_persist_directory=os.getenv("CHROMA_DIR", "chroma_db"),
            default_repos_dir=os.getenv("REPOS_DIR", "data/repos"),
            retriever_k=int(os.getenv("RETRIEVER_K", "4")),
            default_max_files=int(os.getenv("MAX_FILES", "3")),
        )


def validate_environment() -> None:
    """
    Validate that required environment variables are set.

    Raises:
        EnvironmentError: If OPENAI_API_KEY is not set.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. "
            "Create a .env file with OPENAI_API_KEY=sk-... or export it in your shell."
        )
    logger.debug("Environment validation passed.")


# Singleton config instance used across the application
config = Config.from_env()
