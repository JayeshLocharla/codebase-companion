"""
review_chain — orchestrates the full multi-agent analysis pipeline.

Changes from original:
- Adds ingestion step before agents run (critical bug fix)
- Collects and returns all agent outputs instead of discarding them
- Uses logging instead of print()
- Accepts config-driven defaults
"""

import logging
from pathlib import Path

from app.agents.analyzer import AnalyzerAgent
from app.agents.documenter import DocumenterAgent
from app.agents.qa_agent import QAAgent
from app.agents.tester_agent import TesterAgent
from app.agents.readme_agent import ReadmeAgent
from app.core.ingestion import ingest_repository
from app.config import config

logger = logging.getLogger(__name__)


def run_pipeline(
    repo_path: str = None,
    max_files: int = None,
) -> dict:
    """
    Run the full Codebase Companion agent pipeline on a local repository.

    Steps:
        1. Validate the repository path.
        2. Ingest repository files into ChromaDB (REQUIRED before AnalyzerAgent).
        3. Run AnalyzerAgent  → semantic code analysis.
        4. Run DocumenterAgent → function-level docstrings + file summary.
        5. Run QAAgent          → code quality review.
        6. Run TesterAgent      → pytest test generation.
        7. Run ReadmeAgent      → README.md draft.

    Args:
        repo_path: Local path to the cloned repository.
                   Defaults to ``config.default_repos_dir``.
        max_files: Maximum files passed to each agent.
                   Defaults to ``config.default_max_files``.

    Returns:
        Dict mapping section name → output string (suitable for PDF export or display).
    """
    repo_path = repo_path or config.default_repos_dir
    max_files = max_files or config.default_max_files

    logger.info("Starting Codebase Companion pipeline on: %s", repo_path)

    if not Path(repo_path).exists():
        logger.error("Repository path not found: %s", repo_path)
        return {}

    output: dict = {}

    # Step 1 — Ingest repository into ChromaDB (was missing before)
    logger.info("Step 0: Ingesting repository into vector store")
    doc_count = ingest_repository(repo_path, max_files=max_files)
    logger.info("Ingested %d code-block documents", doc_count)

    # Step 2 — Analyzer (uses RAG over ingested docs)
    logger.info("Step 1: Analyzer Agent")
    analyzer = AnalyzerAgent()
    analysis = analyzer.analyze("Find logic issues or code smells")
    output["Analyzer Output"] = analysis

    # Step 3 — Documenter (function-level)
    logger.info("Step 2: Documenter Agent (function-level docstrings)")
    documenter = DocumenterAgent()
    doc_results = documenter.document_functions(code_dir=repo_path, limit=max_files)
    doc_lines = []
    for r in doc_results:
        doc_lines.append(f"{r['type']} `{r['name']}` at line {r['lineno']} in {r['file']}:")
        doc_lines.append(r["docstring"])
        doc_lines.append("")
    output["Documenter Output"] = "\n".join(doc_lines)

    # Step 4 — Documenter (file-level summary for first file)
    from app.utils.file_utils import collect_supported_files
    all_files = collect_supported_files(repo_path)
    if all_files:
        logger.info("Step 2b: Documenter Agent (file-level summary)")
        summary = documenter.summarize_file(filepath=all_files[0])
        output["File Summary"] = summary
    else:
        logger.warning("No supported files found for file-level summary")

    # Step 5 — QA
    logger.info("Step 3: QA Agent")
    qa = QAAgent()
    qa_results = qa.review_codebase(code_dir=repo_path, max_files=max_files)
    qa_lines = []
    for r in qa_results:
        qa_lines.append(f"{r['type']} `{r['name']}` at line {r['lineno']}:")
        qa_lines.append(r["review"])
        qa_lines.append("")
    output["QA Review"] = "\n".join(qa_lines)

    # Step 6 — Tester
    logger.info("Step 4: Tester Agent")
    tester = TesterAgent()
    test_results = tester.generate_tests(code_dir=repo_path, max_files=max_files)
    test_lines = []
    for r in test_results:
        test_lines.append(f"# Test for {r['type']} `{r['name']}` at line {r['lineno']}")
        test_lines.append(r["test_code"])
        test_lines.append("")
    output["Generated Tests"] = "\n".join(test_lines)

    # Step 7 — README
    logger.info("Step 5: README Agent")
    readme = ReadmeAgent()
    output["Generated README"] = readme.generate_readme(code_dir=repo_path)

    logger.info("Pipeline completed. %d sections generated.", len(output))
    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = run_pipeline()
    for section, content in results.items():
        print(f"\n{'='*60}\n{section}\n{'='*60}")
        print(content)
