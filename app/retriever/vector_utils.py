"""
ChromaDB vector store setup.

Reads configuration from ``app.config`` instead of relying on hardcoded
defaults. Adds error handling so a missing or corrupt vector store surfaces
a clear message rather than a cryptic traceback.

Heavy ML dependencies (langchain_huggingface, langchain_chroma) are imported
lazily inside the function body so that importing this module doesn't fail in
environments where those packages are not installed (e.g. during unit tests
that mock get_vectorstore).
"""

import logging

from app.config import config

logger = logging.getLogger(__name__)


def get_vectorstore(
    persist_directory: str = None,
    model_name: str = None,
):
    """
    Return a ChromaDB vector store backed by HuggingFace embeddings.

    Args:
        persist_directory: Directory for ChromaDB persistence.
                           Defaults to ``config.chroma_persist_directory``.
        model_name:        HuggingFace embedding model name.
                           Defaults to ``config.embedding_model``.

    Returns:
        Configured ``Chroma`` instance.

    Raises:
        RuntimeError: If the vector store cannot be initialised.
    """
    # Lazy imports — keep heavy ML packages out of module-level scope so that
    # unit tests that mock get_vectorstore can import this module without them.
    try:
        from langchain_huggingface import HuggingFaceEmbeddings  # noqa: PLC0415
        from langchain_chroma import Chroma  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError(
            "langchain_huggingface and/or langchain_chroma are not installed. "
            "Run: pip install langchain-huggingface langchain-chroma"
        ) from exc

    persist_directory = persist_directory or config.chroma_persist_directory
    model_name = model_name or config.embedding_model

    try:
        embedding_model = HuggingFaceEmbeddings(model_name=model_name)
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model,
        )
        logger.debug("Vector store ready at %s (model: %s)", persist_directory, model_name)
        return vectorstore
    except Exception as exc:
        raise RuntimeError(
            f"Failed to initialise ChromaDB at {persist_directory!r}: {exc}"
        ) from exc
