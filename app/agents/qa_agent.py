"""
QAAgent — code quality review agent.

Reviews code blocks for readability, naming conventions, potential bugs,
PEP 8 compliance, and modularity. Returns structured data rather than printing.
"""

import logging

from app.agents.base_agent import BaseAgent
from app.config import config
from app.utils.file_utils import collect_supported_files
from app.utils.parser import parse_file_by_type

logger = logging.getLogger(__name__)

_PROMPT = """
You are a senior software engineer performing a code quality review.
Review the following Python code and provide feedback on:

- Code readability and structure
- Naming conventions (functions, variables)
- Potential bugs or logic errors
- Style and formatting (PEP8)
- Suggestions for modularity and maintainability

Be concise, professional, and list your feedback in bullet points.

Code:
```python
{code}
```
"""


class QAAgent(BaseAgent):
    """Review code files for quality, style, and potential bugs."""

    def __init__(self) -> None:
        super().__init__(temperature=config.openai_temperature_analysis)
        self._build_chain(_PROMPT)

    def review_codebase(
        self,
        code_dir: str = None,
        max_files: int = None,
    ) -> list[dict]:
        """
        Review code blocks in ``code_dir`` for quality issues.

        Args:
            code_dir:  Path to the repository root. Defaults to config value.
            max_files: Maximum number of files to review.

        Returns:
            List of dicts with keys: file, name, type, lineno, review.
        """
        code_dir = code_dir or config.default_repos_dir
        max_files = max_files or config.default_max_files
        all_files = collect_supported_files(code_dir)
        logger.info("QAAgent: found %d supported files", len(all_files))

        results: list[dict] = []
        for filepath in all_files[:max_files]:
            logger.debug("QAAgent: reviewing %s", filepath)
            blocks = parse_file_by_type(filepath)
            for block in blocks:
                try:
                    review = self._invoke(code=block["code"])
                    results.append(
                        {
                            "file": filepath,
                            "name": block["name"],
                            "type": block["type"],
                            "lineno": block["lineno"],
                            "review": review.strip(),
                        }
                    )
                except Exception as exc:
                    logger.error(
                        "QAAgent: failed on %s in %s — %s",
                        block["name"],
                        filepath,
                        exc,
                    )

        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = QAAgent()
    results = agent.review_codebase(max_files=2)
    for r in results:
        print(f"\n{r['type']} `{r['name']}` at line {r['lineno']}:")
        print(r["review"])
