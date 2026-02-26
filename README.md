# Codebase Companion

> An autonomous AI DevOps assistant that reviews, documents, and tests any GitHub repository using a multi-agent LLM pipeline.

Point it at any public GitHub repo, and five specialised agents will analyse the code, generate docstrings, write unit tests, review quality, and produce a README — all in one run, delivered as an interactive web report or a downloadable PDF.

---

## Table of Contents

1. [How it works](#how-it-works)
2. [Prerequisites](#prerequisites)
3. [Option A — Local setup (recommended)](#option-a--local-setup-recommended)
4. [Option B — Docker setup](#option-b--docker-setup)
5. [Run the web UI](#run-the-web-ui)
6. [Run the CLI](#run-the-cli)
7. [Run the tests](#run-the-tests)
8. [Configuration reference](#configuration-reference)
9. [What each agent does](#what-each-agent-does)
10. [Expected output](#expected-output)
11. [Project structure](#project-structure)
12. [Troubleshooting](#troubleshooting)
13. [Contributing — adding a new agent](#contributing--adding-a-new-agent)
14. [License](#license)

---

## How it works

```
You enter a GitHub URL
        │
        ▼
  download_github_repo()      Clone repo to data/repos/ (cached after first run)
        │
        ▼
  ingest_repository()         Parse .py / .ipynb / .yaml / .md / Dockerfile
        │                     → embed with BAAI/bge-small-en-v1.5
        │                     → store in ChromaDB (persisted to chroma_db/)
        ▼
  ┌─────────────────────────────────────────────────────┐
  │                Multi-Agent Pipeline                  │
  │                                                     │
  │  1. AnalyzerAgent   — RAG: retrieve relevant code   │
  │                        → LLM: find bugs & smells    │
  │  2. DocumenterAgent — generate docstrings per func  │
  │                        + file-level summary         │
  │  3. QAAgent         — review PEP 8, naming, logic   │
  │  4. TesterAgent     — write pytest unit tests       │
  │  5. ReadmeAgent     — draft a README.md             │
  └─────────────────────────────────────────────────────┘
        │
        ▼
  generate_pdf_report()       Bundle all outputs → PDF bytes
        │
        ▼
  Streamlit UI  or  CLI output  or  PDF download
```

**Tech stack:** Python 3.11 · LangChain · OpenAI GPT · ChromaDB · HuggingFace sentence-transformers · Streamlit · ReportLab

---

## Prerequisites

| Requirement | Minimum version | How to check |
|-------------|----------------|--------------|
| Python | 3.11 | `python3 --version` |
| pip | 23+ | `pip --version` |
| git | 2.x | `git --version` |
| OpenAI account | — | [platform.openai.com](https://platform.openai.com) |

> **Docker path only:** Docker 24+ with Compose v2 (`docker compose version`).

You do **not** need a GPU. Embeddings run on CPU using a small HuggingFace model.

---

## Option A — Local setup (recommended)

### 1. Clone the repository

```bash
git clone https://github.com/JayeshLocharla/codebase-companion
cd codebase-companion
```

### 2. Create and activate a Python virtual environment

Using a virtual environment keeps the 150+ dependencies isolated from your system Python.

```bash
# Create the environment
python3 -m venv .venv

# Activate it — run this every time you open a new terminal
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows (cmd)
# .venv\Scripts\Activate.ps1       # Windows (PowerShell)
```

Your prompt will change to show `(.venv)` when activated.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs ~150 packages (LangChain, OpenAI SDK, ChromaDB, Streamlit, PyTorch CPU, etc.).
First run takes 2–5 minutes depending on your internet connection.

**Or use the Makefile shortcut:**

```bash
make install
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` in your editor and set your OpenAI API key:

```dotenv
OPENAI_API_KEY=sk-proj-...your-key-here...
```

Get a key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
The `.env` file is listed in `.gitignore` — it will never be committed.

---

## Option B — Docker setup

No Python installation required. Docker pulls the image and manages all dependencies.

### 1. Clone and configure

```bash
git clone https://github.com/JayeshLocharla/codebase-companion
cd codebase-companion
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

### 2. Build and start

```bash
docker compose up --build
```

The first build takes several minutes (installing PyTorch, transformers, etc.).
Subsequent starts reuse the cached image and are fast.

### 3. Open the UI

Navigate to [http://localhost:8501](http://localhost:8501).

ChromaDB embeddings and cloned repos are stored in Docker named volumes
(`chroma_data`, `repo_cache`) and persist across container restarts.

**Stop the container:**

```bash
docker compose down
```

---

## Run the web UI

**Local (after `make install`):**

```bash
# With Makefile (checks for .env automatically)
make run

# Or directly
source .venv/bin/activate
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501).

**How to use the UI:**

1. Paste a GitHub URL in the **sidebar** (e.g. `https://github.com/pallets/flask`)
2. Leave **Run Full Pipeline** checked to run all 5 agents, or uncheck to pick individual agents
3. Click **Run Analysis**
4. Watch the progress — the app clones the repo, ingests it into ChromaDB, then runs each agent
5. Expand the collapsible sections to read each agent's output
6. Click **Download Full Report (PDF)** to save everything as a single document

---

## Run the CLI

For terminal-only workflows without a browser:

```bash
# With Makefile
make cli

# Or directly
source .venv/bin/activate
python main.py
```

You will be prompted:

```
Codebase Companion
Enter a full GitHub repo URL (e.g. https://github.com/psf/requests):
```

All five agents run sequentially and print their output to the terminal.

---

## Run the tests

The project has **51 unit tests** that run without an OpenAI API key (all LLM calls are mocked).

```bash
# With Makefile
make test

# Or directly
source .venv/bin/activate
pytest tests/ -v
```

Expected output:

```
collected 51 items

tests/test_agents.py::TestAnalyzerAgent::test_analyze_returns_string PASSED
tests/test_agents.py::TestAnalyzerAgent::test_analyze_warns_on_empty_retrieval PASSED
...
======================== 51 passed in 2.5s =========================
```

**With coverage report:**

```bash
make test-cov
# Opens htmlcov/index.html with line-by-line coverage
```

---

## Configuration reference

All values can be set in `.env` or exported as shell variables. The app reads them at startup via `app/config.py`.

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | **required** | Your OpenAI API key (`sk-...`) |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | Chat model. Try `gpt-4o` for higher quality output |
| `RETRIEVER_K` | `4` | Number of code chunks the Analyzer retrieves per query |
| `CHROMA_DIR` | `chroma_db` | Where ChromaDB persists embedding vectors |
| `REPOS_DIR` | `data/repos` | Where cloned repositories are cached |
| `MAX_FILES` | `3` | Max source files each agent processes per run |

**Tips:**

- Delete `chroma_db/` to force a full re-ingestion on the next run
- Delete `data/repos/owner_repo/` to force a fresh clone of a specific repo
- Set `MAX_FILES=10` (and `RETRIEVER_K=8`) for more thorough analysis of larger repos
- Switch to `OPENAI_MODEL=gpt-4o` for significantly better code understanding

---

## What each agent does

| Agent | Input | Output | Cost driver |
|-------|-------|--------|-------------|
| **Analyzer** | Top-K code chunks from ChromaDB (semantic search) | Bullet-point list of bugs, smells, and style issues | 1 LLM call, small context |
| **Documenter** | Each function/class parsed via Python AST | Docstring per function + high-level file summary | N LLM calls (one per code block) |
| **QA** | Raw code blocks from up to `MAX_FILES` files | PEP 8, naming, readability, and logic feedback per block | N LLM calls |
| **Tester** | Raw code blocks | pytest-style unit test functions with edge cases | N LLM calls |
| **README** | Up to 50 code block snippets concatenated | Full Markdown README.md draft | 1 LLM call, large context |

All agents use `gpt-3.5-turbo` by default (cheap, ~$0.002 per run on a small repo).

---

## Expected output

After running on a small Python project you should see output similar to:

**Analyzer:**
```
- Function `process_data` has a nested loop with O(n²) complexity — consider a dict lookup
- Variable `x` in `calculate_score` is a single-letter name with no context
- Missing error handling around the file I/O in `load_config`
```

**Documenter:**
```python
def calculate_score(items: list) -> float:
    """
    Calculate the aggregate score from a list of item values.

    Args:
        items: A list of numeric item values.

    Returns:
        The sum of all item values as a float.
    """
```

**QA:**
```
- Line 42: `getData` should be renamed `get_data` (PEP 8 snake_case)
- Missing type hints on public functions
- `open(filepath)` should use a context manager (`with open(...)`)
```

**Tester:**
```python
def test_calculate_score_empty_list():
    assert calculate_score([]) == 0.0

def test_calculate_score_single_item():
    assert calculate_score([5]) == 5.0
```

**README:** A complete Markdown README with installation, usage, and API docs.

---

## Project structure

```
codebase-companion/
│
├── app/                            Application package
│   ├── config.py                   Central config — reads all env vars, validates API key
│   │
│   ├── agents/                     The five AI agents
│   │   ├── base_agent.py           Abstract base class (shared LLM init, chain building)
│   │   ├── analyzer.py             RAG-based code analysis (requires ChromaDB populated)
│   │   ├── documenter.py           Docstring generator + file summariser
│   │   ├── qa_agent.py             Code quality reviewer
│   │   ├── tester_agent.py         pytest test generator
│   │   └── readme_agent.py         README.md drafter
│   │
│   ├── chains/
│   │   └── review_chain.py         Pipeline orchestrator — runs all agents in order
│   │
│   ├── core/
│   │   └── ingestion.py            Repo → parse → embed → ChromaDB (run before agents!)
│   │
│   ├── retriever/
│   │   └── vector_utils.py         ChromaDB + HuggingFace embeddings setup
│   │
│   └── utils/
│       ├── file_utils.py           Collect supported files (.py .ipynb .yaml .md Dockerfile)
│       ├── github.py               Secure git clone (HTTPS + github.com only)
│       ├── parser.py               Multi-format parser: Python AST, Jupyter, YAML, text
│       ├── pdf_exporter.py         Render agent outputs as PDF bytes (ReportLab)
│       └── torch_patch.py          Fix PyTorch crash on Streamlit hot-reload
│
├── tests/                          pytest test suite (51 tests, no API key needed)
│   ├── conftest.py                 Shared fixtures + fake OPENAI_API_KEY for mocking
│   ├── test_agents.py              All 5 agents tested with mocked LLM calls
│   ├── test_config.py              Config loading and env var validation
│   ├── test_file_utils.py          File collection logic
│   ├── test_github.py              URL validation and clone logic
│   ├── test_ingestion.py           Ingestion pipeline with mocked ChromaDB
│   ├── test_parser.py              AST and text parsers
│   └── test_pdf_exporter.py        PDF byte generation
│
├── main.py                         CLI entry point
├── streamlit_app.py                Streamlit web UI entry point
│
├── .env.example                    Template for environment variables
├── Makefile                        Shortcuts: make install / run / cli / test / clean
├── Dockerfile                      Container image (multi-stage build)
├── docker-compose.yml              docker compose up → Streamlit on :8501
├── pyproject.toml                  Packaging metadata + pytest config
├── requirements.txt                Pinned dependencies
├── ARCHITECTURE_ANALYSIS.md        Full audit report (20 issues found & fixed)
└── LICENSE                         Apache 2.0
```

---

## Troubleshooting

### `EnvironmentError: OPENAI_API_KEY is not set`

You have not created a `.env` file or the key is missing from it.

```bash
cp .env.example .env
# Open .env and set OPENAI_API_KEY=sk-...
```

---

### `ModuleNotFoundError: No module named 'langchain'` (or any other package)

Your virtual environment is not activated, or `pip install -r requirements.txt` was not run inside it.

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

### `ValueError: Unsafe URL scheme 'http'` or `Host '...' is not allowed`

Only `https://github.com` URLs are accepted. Ensure your URL:
- Starts with `https://` (not `http://`)
- Points to `github.com` (not GitLab, Bitbucket, etc.)
- Has exactly `owner/repo` as the path (no trailing slash issue with most URLs is fine)

```
# Good
https://github.com/psf/requests

# Bad
http://github.com/psf/requests        ← http not allowed
https://gitlab.com/user/repo           ← not github.com
```

---

### Streamlit crashes with a PyTorch error on startup

This is a known incompatibility between PyTorch and Streamlit's file watcher. It is patched automatically by `app/utils/torch_patch.py`, which is imported at the top of `streamlit_app.py`.

If you still see it, try:

```bash
STREAMLIT_SERVER_ENABLE_FILE_WATCHING=false streamlit run streamlit_app.py
```

---

### The Analyzer returns "No code was retrieved from the vector store"

This means `ingest_repository()` ran but found zero code blocks, or no Python/supported files exist in the target repository. Try a repo that has `.py` files at the root level.

If you are running agents directly (not through the pipeline), call `ingest_repository(local_path)` before creating an `AnalyzerAgent`.

---

### Docker build fails on `torch` / `onnxruntime`

These packages are large and CPU-only. The build requires ~4 GB of disk space and a stable internet connection. If it times out, retry:

```bash
docker compose build --no-cache
```

---

## Contributing — adding a new agent

1. Create `app/agents/my_agent.py` that extends `BaseAgent`:

```python
from app.agents.base_agent import BaseAgent
from app.config import config

_PROMPT = """
You are an expert. Given this code, do something useful.

Code:
```python
{code}
```
"""

class MyAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(temperature=config.openai_temperature_analysis)
        self._build_chain(_PROMPT)

    def run(self, code_dir: str = None) -> list[dict]:
        # collect files, parse blocks, call self._invoke(code=block["code"])
        ...
```

2. Add it to `app/chains/review_chain.py` in the `run_pipeline()` function.

3. Add a section to `streamlit_app.py` that calls the agent and displays its output.

4. Add tests in `tests/test_agents.py` following the existing pattern (mock `ChatOpenAI`).

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).
