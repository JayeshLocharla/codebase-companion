"""
Agent unit tests using mocked LLM calls.

These tests verify agent logic (prompt building, result structure, error handling)
without making real API calls.

Modules are imported at the top of this file so that unittest.mock.patch can
resolve them by dotted path (patch requires the target module to be in sys.modules
before the patch context manager is entered).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

# Pre-import all agent modules so patch() can resolve them by dotted-path string.
import app.agents.analyzer
import app.agents.documenter
import app.agents.qa_agent
import app.agents.tester_agent
import app.agents.readme_agent

from app.agents.analyzer import AnalyzerAgent
from app.agents.documenter import DocumenterAgent
from app.agents.qa_agent import QAAgent
from app.agents.tester_agent import TesterAgent
from app.agents.readme_agent import ReadmeAgent


# ── AnalyzerAgent ─────────────────────────────────────────────────────────────

class TestAnalyzerAgent:
    def test_analyze_returns_string(self):
        fake_doc = MagicMock()
        fake_doc.page_content = "def foo(): pass"

        mock_vs = MagicMock()
        mock_vs.as_retriever.return_value.invoke.return_value = [fake_doc]

        with patch("app.agents.analyzer.get_vectorstore", return_value=mock_vs), \
             patch("app.agents.base_agent.ChatOpenAI"):
            agent = AnalyzerAgent()
            agent.chain = MagicMock()
            agent.chain.invoke.return_value = "Found 1 issue."
            result = agent.analyze("Find issues")

        assert isinstance(result, str)

    def test_analyze_warns_on_empty_retrieval(self):
        mock_vs = MagicMock()
        mock_vs.as_retriever.return_value.invoke.return_value = []

        with patch("app.agents.analyzer.get_vectorstore", return_value=mock_vs), \
             patch("app.agents.base_agent.ChatOpenAI"):
            agent = AnalyzerAgent()
            result = agent.analyze("Find issues")

        assert "No code was retrieved" in result


# ── DocumenterAgent ───────────────────────────────────────────────────────────

class TestDocumenterAgent:
    def test_document_functions_returns_list(self, tmp_path: Path):
        (tmp_path / "sample.py").write_text("def hello(): pass\n")

        with patch("app.agents.base_agent.ChatOpenAI"), \
             patch("app.agents.documenter.StrOutputParser"):
            agent = DocumenterAgent()
            agent.chain = MagicMock()
            agent.chain.invoke.return_value = '"""Does something."""'
            agent._summary_chain = MagicMock()

            results = agent.document_functions(code_dir=str(tmp_path), limit=1)

        assert isinstance(results, list)
        for r in results:
            assert "name" in r
            assert "docstring" in r
            assert "file" in r

    def test_summarize_file_returns_string(self, tmp_path: Path):
        p = tmp_path / "mod.py"
        p.write_text("def foo(): pass\n")

        with patch("app.agents.base_agent.ChatOpenAI"):
            agent = DocumenterAgent()
            agent._summary_chain = MagicMock()
            agent._summary_chain.invoke.return_value = "Summary text."

            result = agent.summarize_file(str(p))

        assert isinstance(result, str)

    def test_summarize_file_returns_warning_for_empty_file(self, tmp_path: Path):
        p = tmp_path / "empty.py"
        p.write_text("")  # No functions/classes → parse returns []

        with patch("app.agents.base_agent.ChatOpenAI"):
            agent = DocumenterAgent()
            result = agent.summarize_file(str(p))

        assert "No code blocks" in result


# ── QAAgent ───────────────────────────────────────────────────────────────────

class TestQAAgent:
    def test_review_codebase_returns_list_of_dicts(self, tmp_path: Path):
        (tmp_path / "code.py").write_text("def foo(): pass\n")

        with patch("app.agents.base_agent.ChatOpenAI"):
            agent = QAAgent()
            agent.chain = MagicMock()
            agent.chain.invoke.return_value = "- Code looks good."

            results = agent.review_codebase(code_dir=str(tmp_path), max_files=1)

        assert isinstance(results, list)
        for r in results:
            assert "review" in r
            assert "name" in r


# ── TesterAgent ───────────────────────────────────────────────────────────────

class TestTesterAgent:
    def test_generate_tests_returns_list_of_dicts(self, tmp_path: Path):
        (tmp_path / "funcs.py").write_text("def add(a, b): return a + b\n")

        with patch("app.agents.base_agent.ChatOpenAI"):
            agent = TesterAgent()
            agent.chain = MagicMock()
            agent.chain.invoke.return_value = "def test_add(): assert add(1,2)==3"

            results = agent.generate_tests(code_dir=str(tmp_path), max_files=1)

        assert isinstance(results, list)
        for r in results:
            assert "test_code" in r


# ── ReadmeAgent ───────────────────────────────────────────────────────────────

class TestReadmeAgent:
    def test_generate_readme_returns_string(self, tmp_path: Path):
        (tmp_path / "app.py").write_text("def main(): pass\n")

        with patch("app.agents.base_agent.ChatOpenAI"):
            agent = ReadmeAgent()
            agent.chain = MagicMock()
            agent.chain.invoke.return_value = "# My Project\n..."

            result = agent.generate_readme(code_dir=str(tmp_path))

        assert isinstance(result, str)

    def test_generate_readme_handles_empty_dir(self, tmp_path: Path):
        with patch("app.agents.base_agent.ChatOpenAI"):
            agent = ReadmeAgent()
            result = agent.generate_readme(code_dir=str(tmp_path))

        assert "No code blocks" in result
