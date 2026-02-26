"""
AnalyzerAgent — semantic code analysis using a RAG pattern.

Retrieves the most relevant code chunks from ChromaDB (populated by
``app.core.ingestion.ingest_repository``) and passes them to the LLM for
analysis.  Requires the vector store to be populated before instantiation.
"""

import logging

from app.retriever.vector_utils import get_vectorstore
from app.agents.base_agent import BaseAgent
from app.config import config

logger = logging.getLogger(__name__)

_PROMPT = """
You are a senior software engineer reviewing a codebase.
Analyze the following code for:
- Readability issues
- Performance or logic bugs
- Poor naming, modularity, or style
Provide actionable and concise feedback in bullet points.

Code to analyze:
```python
{code}
```
"""


class AnalyzerAgent(BaseAgent):
    """Analyze retrieved code chunks for bugs, smells, and style issues."""

    def __init__(self) -> None:
        super().__init__(temperature=config.openai_temperature_analysis)
        vectorstore = get_vectorstore()
        self.retriever = vectorstore.as_retriever(
            search_kwargs={"k": config.retriever_k}
        )
        self._build_chain(_PROMPT)

    def analyze(self, query: str) -> str:
        """
        Run semantic search for ``query`` then analyse the retrieved code.

        Args:
            query: A natural-language description of what to look for
                   (e.g. "Find logic issues or code smells").

        Returns:
            LLM analysis as a formatted string.
        """
        docs = self.retriever.invoke(query)
        if not docs:
            logger.warning("AnalyzerAgent: no documents retrieved for query %r", query)
            return "No code was retrieved from the vector store. Run ingestion first."
        combined_code = "\n\n".join(doc.page_content for doc in docs)
        logger.info("AnalyzerAgent: analysing %d retrieved code chunks", len(docs))
        return self._invoke(code=combined_code)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = AnalyzerAgent()
    result = agent.analyze("Find complex or hard-to-read logic")
    print(result)
