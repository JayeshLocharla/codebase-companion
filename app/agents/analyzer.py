import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()  # Load OPENAI_API_KEY from .env


class AnalyzerAgent:
    def __init__(self):
        # Load embedding model for retrieval
        self.embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

        # Connect to ChromaDB
        self.vectorstore = Chroma(
            persist_directory="chroma_db",
            embedding_function=self.embedding_model
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})

        # Prompt template for the LLM
        self.prompt = PromptTemplate.from_template("""
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
        """)

        # LLM to generate the analysis
        self.llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")

        # Combine steps into a runnable chain
        self.chain: Runnable = self.prompt | self.llm | StrOutputParser()

    def analyze(self, query: str):
        """Run the analyzer on a semantic query."""
        docs = self.retriever.invoke(query)
        combined_code = "\n\n".join([doc.page_content for doc in docs])
        return self.chain.invoke({"code": combined_code})


# ✅ Test block (for dev only)
if __name__ == "__main__":
    print("🤖 Analyzer Agent Starting...")
    agent = AnalyzerAgent()
    response = agent.analyze("Find complex or hard-to-read logic")
    print("\n🔍 ANALYZER OUTPUT:\n")
    print(response)
