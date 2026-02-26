"""
DocumenterAgent — generates docstrings and file-level summaries.

Returns structured data instead of printing, so callers (CLI, Streamlit, tests)
can handle output in whatever way suits them.
"""

import logging

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.agents.base_agent import BaseAgent
from app.config import config
from app.utils.file_utils import collect_supported_files
from app.utils.parser import parse_file_by_type

logger = logging.getLogger(__name__)

_DOCSTRING_PROMPT = """
You are a Python expert. Given the following function or class, generate a clean,
professional docstring using triple double quotes.

Rules:
- Explain what it does
- Include parameters (if any)
- Mention return values (if applicable)
- Be brief and accurate

Code:
```python
{code}
```
"""

_SUMMARY_PROMPT = """
You are a senior software engineer. Given this Python file content, summarize:

- Its purpose
- Key classes/functions
- Notable dependencies or imports

File contents:
```python
{code}
```
"""


class DocumenterAgent(BaseAgent):
    """Generate docstrings for functions/classes and file-level summaries."""

    def __init__(self) -> None:
        super().__init__(temperature=config.openai_temperature_generation)
        self._build_chain(_DOCSTRING_PROMPT)
        # Build a separate chain for file summaries (different prompt, same LLM)
        summary_prompt = PromptTemplate.from_template(_SUMMARY_PROMPT)
        self._summary_chain = summary_prompt | self.llm | StrOutputParser()

    def document_functions(
        self,
        code_dir: str = None,
        limit: int = 5,
    ) -> list[dict]:
        """
        Generate docstrings for functions and classes in ``code_dir``.

        Args:
            code_dir: Path to the repository root. Defaults to config value.
            limit:    Maximum number of files to process.

        Returns:
            List of dicts with keys: file, name, type, lineno, docstring.
        """
        code_dir = code_dir or config.default_repos_dir
        all_files = collect_supported_files(code_dir)
        logger.info("DocumenterAgent: found %d supported files", len(all_files))

        results: list[dict] = []
        for filepath in all_files[:limit]:
            logger.debug("DocumenterAgent: documenting %s", filepath)
            blocks = parse_file_by_type(filepath)
            for block in blocks:
                try:
                    docstring = self._invoke(code=block["code"])
                    results.append(
                        {
                            "file": filepath,
                            "name": block["name"],
                            "type": block["type"],
                            "lineno": block["lineno"],
                            "docstring": docstring.strip(),
                        }
                    )
                except Exception as exc:
                    logger.error(
                        "DocumenterAgent: failed on %s in %s — %s",
                        block["name"],
                        filepath,
                        exc,
                    )

        return results

    def summarize_file(self, filepath: str) -> str:
        """
        Generate a high-level summary of a Python file's purpose and structure.

        Args:
            filepath: Path to the Python file.

        Returns:
            Summary string, or a warning message if no code blocks found.
        """
        blocks = parse_file_by_type(filepath)
        if not blocks:
            logger.warning("DocumenterAgent: no code blocks in %s", filepath)
            return f"No code blocks found in: {filepath}"

        full_code = "\n\n".join(block["code"] for block in blocks)
        try:
            summary = self._summary_chain.invoke({"code": full_code})
            logger.info("DocumenterAgent: summarized %s", filepath)
            return summary.strip()
        except Exception as exc:
            logger.error("DocumenterAgent: failed to summarize %s — %s", filepath, exc)
            return f"Failed to summarize file: {exc}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = DocumenterAgent()

    results = agent.document_functions(limit=1)
    for r in results:
        print(f"\n{r['type']} `{r['name']}` at line {r['lineno']}:")
        print(r["docstring"])

    all_files = collect_supported_files(config.default_repos_dir)
    if all_files:
        print("\n--- File Summary ---")
        print(agent.summarize_file(all_files[0]))
