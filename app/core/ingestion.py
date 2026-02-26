"""
Repository ingestion pipeline.

This module is responsible for populating the ChromaDB vector store with
code blocks extracted from a target repository. It MUST be called before
any agent that relies on semantic retrieval (currently AnalyzerAgent).

Previously this step was missing entirely, which meant the vector store was
always empty and the AnalyzerAgent analyzed an empty string on every run.
"""

import logging
from pathlib import Path

from langchain_core.documents import Document

from app.retriever.vector_utils import get_vectorstore
from app.utils.file_utils import collect_supported_files
from app.utils.parser import parse_file_by_type

logger = logging.getLogger(__name__)


def ingest_repository(repo_path: str, max_files: int | None = None) -> int:
    """
    Parse all supported files in ``repo_path`` and add them to ChromaDB.

    This function must be called once per analysis session before agents run.
    It is idempotent — re-ingesting the same content produces duplicate
    embeddings in ChromaDB. Callers that need idempotency should clear the
    collection first or check if ingestion has already been performed.

    Args:
        repo_path: Absolute or relative path to the cloned repository root.
        max_files:  If set, limit ingestion to the first N files found.
                    Useful for large repositories or quick testing.

    Returns:
        The number of code-block documents ingested.

    Raises:
        FileNotFoundError: If ``repo_path`` does not exist.
    """
    if not Path(repo_path).exists():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    vectorstore = get_vectorstore()
    all_files = collect_supported_files(repo_path)

    if max_files is not None:
        all_files = all_files[:max_files]

    logger.info("Ingesting %d files from %s", len(all_files), repo_path)

    documents: list[Document] = []
    for filepath in all_files:
        try:
            blocks = parse_file_by_type(filepath)
        except Exception as exc:
            logger.warning("Failed to parse %s: %s", filepath, exc)
            continue

        for block in blocks:
            code = block.get("code", "").strip()
            if not code:
                continue
            documents.append(
                Document(
                    page_content=code,
                    metadata={
                        "name": block.get("name", "unknown"),
                        "type": block.get("type", "unknown"),
                        "file": block.get("file", filepath),
                        "lineno": block.get("lineno", 0),
                        "source": block.get("source", "unknown"),
                    },
                )
            )

    if documents:
        vectorstore.add_documents(documents)
        logger.info("Ingested %d code-block documents into ChromaDB", len(documents))
    else:
        logger.warning("No code blocks found in %s — vector store is empty", repo_path)

    return len(documents)
