# Codebase Companion

An autonomous AI DevOps assistant that reviews, documents, and tests your GitHub repositories using a multi-agent LLM pipeline.

## Features

| Agent | What it does |
|-------|-------------|
| **Analyzer** | Semantic code analysis via RAG — finds bugs, smells, and style issues |
| **Documenter** | Generates docstrings for functions/classes and file-level summaries |
| **QA** | Reviews code for readability, PEP 8, naming, and potential bugs |
| **Tester** | Generates pytest-style unit tests with edge cases |
| **README** | Drafts a professional README.md from the codebase context |

## Architecture

```
GitHub URL
    │
    ▼
download_github_repo()         # clone repo locally (HTTPS + github.com only)
    │
    ▼
ingest_repository()            # parse files → embed → store in ChromaDB
    │
    ▼
┌───────────────────────┐
│  Multi-Agent Pipeline │
│  AnalyzerAgent  (RAG) │  ← queries ChromaDB for relevant code
│  DocumenterAgent      │
│  QAAgent              │
│  TesterAgent          │
│  ReadmeAgent          │
└───────────────────────┘
    │
    ▼
generate_pdf_report()          # collect outputs → return PDF bytes
```

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/JayeshLocharla/codebase-companion
cd codebase-companion
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

Or export it directly:

```bash
export OPENAI_API_KEY="sk-..."
```

### 3. Run the CLI

```bash
python main.py
# Prompt: Enter a full GitHub repo URL (e.g. https://github.com/psf/requests)
```

### 4. Run the Streamlit web UI

```bash
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser, paste a GitHub URL, select agents, and click **Run Analysis**.

## Configuration

All tunable parameters can be set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | OpenAI API key |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | LLM model name |
| `CHROMA_DIR` | `chroma_db` | ChromaDB persistence directory |
| `REPOS_DIR` | `data/repos` | Local directory for cloned repos |
| `RETRIEVER_K` | `4` | Number of code chunks retrieved by AnalyzerAgent |
| `MAX_FILES` | `3` | Default file limit per pipeline run |

## Project Structure

```
codebase-companion/
├── app/
│   ├── agents/
│   │   ├── base_agent.py       # Abstract base class for all agents
│   │   ├── analyzer.py         # RAG-based code analysis
│   │   ├── documenter.py       # Docstring + file summary generation
│   │   ├── qa_agent.py         # Code quality review
│   │   ├── tester_agent.py     # Unit test generation
│   │   └── readme_agent.py     # README generation
│   ├── chains/
│   │   └── review_chain.py     # Full pipeline orchestrator
│   ├── core/
│   │   └── ingestion.py        # Repository → ChromaDB ingestion
│   ├── retriever/
│   │   └── vector_utils.py     # ChromaDB setup
│   ├── utils/
│   │   ├── file_utils.py       # Supported file collection
│   │   ├── github.py           # Secure GitHub repo cloning
│   │   ├── parser.py           # Multi-format code parser (AST, Jupyter, YAML)
│   │   ├── pdf_exporter.py     # PDF report generation (returns bytes)
│   │   └── torch_patch.py      # PyTorch/Streamlit compatibility fix
│   └── config.py               # Central configuration + env validation
├── tests/                      # pytest test suite
├── main.py                     # CLI entry point
├── streamlit_app.py            # Web UI entry point
├── ARCHITECTURE_ANALYSIS.md    # Full audit report
└── requirements.txt
```

## Running Tests

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=term-missing
```

## Security

- Only `https://github.com` URLs are accepted for cloning — `file://`, `ssh://`, and non-GitHub hosts are blocked.
- The `OPENAI_API_KEY` is read from `.env` and is never logged or printed.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
