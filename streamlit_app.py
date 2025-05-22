# ✅ Fix for torch.classes crash on Streamlit reload
from app.utils.torch_patch import *


import streamlit as st
import os
import io
import contextlib

from app.utils.github import download_github_repo
from app.agents.analyzer import AnalyzerAgent
from app.agents.documenter import DocumenterAgent
from app.agents.qa_agent import QAAgent
from app.agents.tester_agent import TesterAgent
from app.agents.readme_agent import ReadmeAgent
from app.utils.pdf_exporter import generate_pdf_report


# Streamlit UI setup
st.set_page_config(page_title="Codebase Companion", layout="wide")
st.title("🤖 Codebase Companion")
st.markdown("A multi-agent system that reviews, documents, and tests your codebase using LLMs.")

# Sidebar: Repo input + agent selection
st.sidebar.title("📂 Analyze a GitHub Repo")
repo_url = st.sidebar.text_input("🔗 GitHub Repo URL", placeholder="https://github.com/user/repo")
run_all = st.sidebar.checkbox("✅ Run Full Pipeline", value=True)

agent_options = ["Analyzer", "Documenter", "QA", "Tester", "README"]
selected_agents = agent_options if run_all else st.sidebar.multiselect("Select Agents to Run", agent_options)

# Run button
if repo_url and st.sidebar.button("🚀 Run Analysis"):
    with st.spinner("📥 Cloning repository and running agents..."):
        try:
            local_path = download_github_repo(repo_url)
            st.success(f"✅ Repository cloned to: `{local_path}`")

            # Store all outputs in a dict
            output = {}

            # === Analyzer Agent ===
            if "Analyzer" in selected_agents:
                with st.expander("🧠 Analyzer Output", expanded=True):
                    agent = AnalyzerAgent()
                    result = agent.analyze("Find logic issues or code smells")
                    st.markdown(result)
                    output["Analyzer Output"] = result

            # === Documenter Agent ===
            if "Documenter" in selected_agents:
                with st.expander("📘 Documenter Output", expanded=True):
                    agent = DocumenterAgent()

                    # Function-level
                    st.markdown("**Function-level docstrings:**")
                    doc_buffer = io.StringIO()
                    with contextlib.redirect_stdout(doc_buffer):
                        agent.document_functions(code_dir=local_path, limit=3)
                    doc_output = doc_buffer.getvalue()
                    st.code(doc_output, language="markdown")
                    output["Documenter Output"] = doc_output

                    # File-level
                    st.markdown("---")
                    st.markdown("**File-level summary:**")
                    py_files = [f for f in os.listdir(local_path) if f.endswith(".py")]
                    if py_files:
                        agent.summarize_file(filepath=os.path.join(local_path, py_files[0]))

            # === QA Agent ===
            if "QA" in selected_agents:
                with st.expander("🧪 QA Review", expanded=True):
                    agent = QAAgent()
                    qa_buffer = io.StringIO()
                    with contextlib.redirect_stdout(qa_buffer):
                        agent.review_codebase(code_dir=local_path, max_files=3)
                    qa_output = qa_buffer.getvalue()
                    st.code(qa_output, language="markdown")
                    output["QA Review"] = qa_output

            # === Tester Agent ===
            if "Tester" in selected_agents:
                with st.expander("🧬 Generated Tests", expanded=True):
                    agent = TesterAgent()
                    test_buffer = io.StringIO()
                    with contextlib.redirect_stdout(test_buffer):
                        agent.generate_tests(code_dir=local_path, max_files=2)
                    test_output = test_buffer.getvalue()
                    st.code(test_output, language="python")
                    output["Generated Tests"] = test_output

            # === README Agent ===
            if "README" in selected_agents:
                with st.expander("📄 Generated README", expanded=True):
                    agent = ReadmeAgent()
                    result = agent.generate_readme(code_dir=local_path)
                    st.code(result, language="markdown")
                    output["Generated README"] = result
                    
            # 📄 Download PDF Report
            if output:
                with st.expander("📥 Download Report"):
                    pdf_path = generate_pdf_report(output)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📄 Download Full Report (PDF)",
                            data=f,
                            file_name="codebase_report.pdf",
                            mime="application/pdf"
                        )

        except Exception as e:
            st.error(f"❌ Error during pipeline execution:\n\n{e}")



