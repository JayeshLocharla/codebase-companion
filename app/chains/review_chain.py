import os
import glob

from app.agents.analyzer import AnalyzerAgent
from app.agents.documenter import DocumenterAgent
from app.agents.qa_agent import QAAgent
from app.agents.tester_agent import TesterAgent
from app.agents.readme_agent import ReadmeAgent
from app.utils.file_utils import collect_supported_files


def run_pipeline(repo_path="data/repos", max_files=3):
    print("🚀 Running Codebase Companion Full Agent Pipeline")
    print(f"📁 Target repo: {repo_path}\n")

    # Validate repo path
    if not os.path.exists(repo_path):
        print(f"❌ Repo path not found: {repo_path}")
        return

    # Analyzer
    print("\n🧠 Step 1: Analyzer Agent")
    analyzer = AnalyzerAgent()
    analyzer.analyze("Find logic issues or code smells")

    # Documenter — function level
    print("\n📘 Step 2: Documenter Agent (function-level docstrings)")
    documenter = DocumenterAgent()
    documenter.document_functions(code_dir=repo_path, limit=max_files)

    # Documenter — file-level
    print("\n📘 Step 2b: Documenter Agent (file-level summary)")
    all_files = collect_supported_files(repo_path)
    if all_files:
        documenter.summarize_file(filepath=all_files[0])
    else:
        print("⚠️ No supported files found for summary.")


    # QA
    print("\n🧪 Step 3: QA Agent")
    qa = QAAgent()
    qa.review_codebase(code_dir=repo_path, max_files=max_files)

    # Tester
    print("\n🧬 Step 4: Tester Agent")
    tester = TesterAgent()
    tester.generate_tests(code_dir=repo_path, max_files=max_files)

    # README
    print("\n📄 Step 5: README Agent")
    readme = ReadmeAgent()
    readme_md = readme.generate_readme(code_dir=repo_path)
    print("\n📄 Generated README:\n")
    print(readme_md)

    print("\n✅ Pipeline Completed.")


if __name__ == "__main__":
    run_pipeline()
