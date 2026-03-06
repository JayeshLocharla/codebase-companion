"""
ReadmeAgent — generates a professional README.md from codebase context.
"""

import logging

from app.agents.base_agent import BaseAgent
from app.config import config
from app.utils.file_utils import collect_supported_files
from app.utils.parser import parse_file_by_type

logger = logging.getLogger(__name__)

_PROMPT = """
You are a senior software engineer and technical writer.
Given this codebase context, write a professional-level README.md draft.

Include:
- Project title and purpose
- Key modules and features
- How to install and run
- Example usage
- Testing and contribution instructions

Be concise, clear, and helpful for new developers.

Codebase summary:
```python
{code}
```
"""


class ReadmeAgent(BaseAgent):
    """Generate a professional README.md from codebase code blocks."""

    def __init__(self) -> None:
        super().__init__(temperature=config.openai_temperature_generation)
        self._build_chain(_PROMPT)

    def generate_readme(
        self,
        code_dir: str = None,
        max_blocks: int = None,
    ) -> str:
        """
        Generate a README.md draft from the code found in ``code_dir``.

        Args:
            code_dir:   Path to the repository root. Defaults to config value.
            max_blocks: Cap on the number of code blocks included in the prompt.
                        Defaults to config value.

        Returns:
            Generated README content as a string.
        """
        code_dir = code_dir or config.default_repos_dir
        max_blocks = max_blocks or config.default_max_blocks

        all_files = collect_supported_files(code_dir)
        logger.info("ReadmeAgent: found %d supported files", len(all_files))

        all_block_texts: list[str] = []
        for filepath in all_files:
            blocks = parse_file_by_type(filepath)
            all_block_texts.extend(block["code"] for block in blocks)

        if not all_block_texts:
            return "No code blocks found to generate README."

        used = min(max_blocks, len(all_block_texts))
        logger.info("ReadmeAgent: using %d code blocks for README generation", used)
        full_context = "\n\n".join(all_block_texts[:max_blocks])

        try:
            return self._invoke(code=full_context).strip()
        except Exception as exc:
            logger.error("ReadmeAgent: failed to generate README — %s", exc)
            return f"Failed to generate README: {exc}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = ReadmeAgent()
    print(agent.generate_readme())
