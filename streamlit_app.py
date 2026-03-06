# Apply the PyTorch/Streamlit compatibility patch before any other imports.
# Using a plain import (not wildcard) makes the intent (side-effects only) explicit.
import app.utils.torch_patch  # noqa: F401

import logging

import streamlit as st

from app.config import validate_environment
from app.utils.github import download_github_repo
from app.core.ingestion import ingest_repository
from app.agents.analyzer import AnalyzerAgent
from app.agents.documenter import DocumenterAgent
from app.agents.qa_agent import QAAgent
from app.agents.tester_agent import TesterAgent
from app.agents.readme_agent import ReadmeAgent
from app.utils.pdf_exporter import generate_pdf_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Codebase Companion", layout="wide")
st.title("Codebase Companion")
st.markdown("A multi-agent system that reviews, documents, and tests your codebase using LLMs.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Analyze a GitHub Repo")
repo_url = st.sidebar.text_input(
    "GitHub Repo URL",
    placeholder="https://github.com/user/repo",
)
run_all = st.sidebar.checkbox("Run Full Pipeline", value=True)

agent_options = ["Analyzer", "Documenter", "QA", "Tester", "README"]
selected_agents = (
    agent_options
    if run_all
    else st.sidebar.multiselect("Select Agents to Run", agent_options)
)

# ── Run ───────────────────────────────────────────────────────────────────────
if repo_url and st.sidebar.button("Run Analysis"):
    with st.spinner("Cloning repository and running agents..."):
        try:
            validate_environment()
            local_path = download_github_repo(repo_url)
            st.success(f"Repository cloned to: `{local_path}`")

            # Ingest repository into ChromaDB before agents run
            with st.status("Ingesting repository into vector store..."):
                doc_count = ingest_repository(local_path)
                st.write(f"Ingested {doc_count} code-block documents.")

            output: dict = {}

            # ── Analyzer ─────────────────────────────────────────────────────
            if "Analyzer" in selected_agents:
                with st.expander("Analyzer Output", expanded=True):
                    agent = AnalyzerAgent()
                    result = agent.analyze("Find logic issues or code smells")
                    st.markdown(result)
                    output["Analyzer Output"] = result

            # ── Documenter ────────────────────────────────────────────────────
            if "Documenter" in selected_agents:
                with st.expander("Documenter Output", expanded=True):
                    agent = DocumenterAgent()

                    st.markdown("**Function-level docstrings:**")
                    doc_results = agent.document_functions(code_dir=local_path, limit=3)
                    doc_text_parts = []
                    for r in doc_results:
                        header = f"{r['type']} `{r['name']}` at line {r['lineno']}"
                        st.markdown(f"**{header}**")
                        st.code(r["docstring"], language="python")
                        doc_text_parts.append(f"{header}\n{r['docstring']}\n")
                    output["Documenter Output"] = "\n".join(doc_text_parts)

                    st.markdown("---")
                    st.markdown("**File-level summary:**")
                    import os
                    py_files = [f for f in os.listdir(local_path) if f.endswith(".py")]
                    if py_files:
                        summary = agent.summarize_file(
                            filepath=os.path.join(local_path, py_files[0])
                        )
                        st.markdown(summary)
                        output["File Summary"] = summary

            # ── QA ────────────────────────────────────────────────────────────
            if "QA" in selected_agents:
                with st.expander("QA Review", expanded=True):
                    agent = QAAgent()
                    qa_results = agent.review_codebase(code_dir=local_path, max_files=3)
                    qa_text_parts = []
                    for r in qa_results:
                        header = f"{r['type']} `{r['name']}` at line {r['lineno']}"
                        st.markdown(f"**{header}**")
                        st.code(r["review"], language="markdown")
                        qa_text_parts.append(f"{header}\n{r['review']}\n")
                    output["QA Review"] = "\n".join(qa_text_parts)

            # ── Tester ────────────────────────────────────────────────────────
            if "Tester" in selected_agents:
                with st.expander("Generated Tests", expanded=True):
                    agent = TesterAgent()
                    test_results = agent.generate_tests(code_dir=local_path, max_files=2)
                    test_text_parts = []
                    for r in test_results:
                        header = f"Test for {r['type']} `{r['name']}` at line {r['lineno']}"
                        st.markdown(f"**{header}**")
                        st.code(r["test_code"], language="python")
                        test_text_parts.append(f"# {header}\n{r['test_code']}\n")
                    output["Generated Tests"] = "\n".join(test_text_parts)

            # ── README ────────────────────────────────────────────────────────
            if "README" in selected_agents:
                with st.expander("Generated README", expanded=True):
                    agent = ReadmeAgent()
                    result = agent.generate_readme(code_dir=local_path)
                    st.code(result, language="markdown")
                    output["Generated README"] = result

            # ── PDF Download ──────────────────────────────────────────────────
            if output:
                with st.expander("Download Report"):
                    pdf_bytes = generate_pdf_report(output)
                    st.download_button(
                        label="Download Full Report (PDF)",
                        data=pdf_bytes,
                        file_name="codebase_report.pdf",
                        mime="application/pdf",
                    )

        except EnvironmentError as exc:
            st.error(f"Configuration error: {exc}")
        except ValueError as exc:
            st.error(f"Invalid input: {exc}")
        except Exception as exc:
            st.error(f"Error during pipeline execution:\n\n{exc}")
            logging.exception("Unexpected error in Streamlit pipeline")
