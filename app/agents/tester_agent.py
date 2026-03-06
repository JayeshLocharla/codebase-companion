"""
TesterAgent — generates pytest-style unit tests for code blocks.

Returns structured data (list of dicts) rather than printing, allowing
callers to handle output formatting themselves.
"""

import logging

from app.agents.base_agent import BaseAgent
from app.config import config
from app.utils.file_utils import collect_supported_files
from app.utils.parser import parse_file_by_type

logger = logging.getLogger(__name__)

_PROMPT = """
You are a Python testing expert.
Given a function or class, write a unit test in `pytest` style.

Guidelines:
- Use realistic inputs and edge cases
- Focus on correctness and coverage
- Add mock data if needed
- Only return the test function, no explanations

Code to test:
```python
{code}
```
"""


class TesterAgent(BaseAgent):
    """Generate pytest-style unit tests for functions and classes."""

    def __init__(self) -> None:
        super().__init__(temperature=config.openai_temperature_analysis)
        self._build_chain(_PROMPT)

    def generate_tests(
        self,
        code_dir: str = None,
        max_files: int = None,
    ) -> list[dict]:
        """
        Generate unit tests for code blocks found in ``code_dir``.

        Args:
            code_dir:  Path to the repository root. Defaults to config value.
            max_files: Maximum number of files to process.

        Returns:
            List of dicts with keys: file, name, type, lineno, test_code.
        """
        code_dir = code_dir or config.default_repos_dir
        max_files = max_files or config.default_max_files
        all_files = collect_supported_files(code_dir)
        logger.info("TesterAgent: found %d supported files", len(all_files))

        results: list[dict] = []
        for filepath in all_files[:max_files]:
            logger.debug("TesterAgent: generating tests for %s", filepath)
            blocks = parse_file_by_type(filepath)
            for block in blocks:
                try:
                    test_code = self._invoke(code=block["code"])
                    results.append(
                        {
                            "file": filepath,
                            "name": block["name"],
                            "type": block["type"],
                            "lineno": block["lineno"],
                            "test_code": test_code.strip(),
                        }
                    )
                except Exception as exc:
                    logger.error(
                        "TesterAgent: failed on %s in %s — %s",
                        block["name"],
                        filepath,
                        exc,
                    )

        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = TesterAgent()
    results = agent.generate_tests(max_files=2)
    for r in results:
        print(f"\nTest for {r['type']} `{r['name']}` at line {r['lineno']}:")
        print(r["test_code"])
