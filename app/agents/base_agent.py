"""
BaseAgent — abstract base class for all Codebase Companion agents.

Centralises:
- environment setup (dotenv, TOKENIZERS_PARALLELISM)
- LLM instantiation (one shared pattern, configurable via Config)
- LangChain chain construction
- safe LLM invocation with structured error handling and logging
"""

import os
import logging
from abc import ABC

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import config

# Suppress HuggingFace tokenizer parallelism warnings once, at module load time
os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class shared by all agents.

    Subclasses call ``_build_chain(prompt_template)`` in their ``__init__``
    to create ``self.chain``, then use ``_invoke(**kwargs)`` to call the LLM
    safely with logging and error propagation.
    """

    def __init__(self, temperature: float | None = None) -> None:
        resolved_temp = temperature if temperature is not None else config.openai_temperature_analysis
        self.llm = ChatOpenAI(
            model=config.openai_model,
            temperature=resolved_temp,
        )
        self._output_parser = StrOutputParser()
        self.chain = None

    def _build_chain(self, prompt_template: str):
        """
        Build and store a LangChain runnable chain from a prompt template string.

        Args:
            prompt_template: A LangChain-compatible prompt template string.

        Returns:
            The constructed chain (also stored as ``self.chain``).
        """
        prompt = PromptTemplate.from_template(prompt_template)
        self.chain = prompt | self.llm | self._output_parser
        return self.chain

    def _invoke(self, **kwargs) -> str:
        """
        Invoke ``self.chain`` with the given keyword arguments.

        Args:
            **kwargs: Variables injected into the prompt template.

        Returns:
            The LLM response as a string.

        Raises:
            RuntimeError: If ``_build_chain`` was never called.
            Exception: Re-raises any LLM/network exception after logging it.
        """
        if self.chain is None:
            raise RuntimeError(
                f"{type(self).__name__}: call _build_chain() before _invoke()."
            )
        try:
            return self.chain.invoke(kwargs)
        except Exception as exc:
            logger.error("%s: LLM invocation failed — %s", type(self).__name__, exc)
            raise
