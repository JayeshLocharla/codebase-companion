import os
from dotenv import load_dotenv
from glob import glob

from langchain_openai import ChatOpenAI
from app.retriever.vector_utils import get_vectorstore
from langchain.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from app.utils.file_utils import collect_supported_files


from app.utils.parser import parse_file_by_type  # make sure this exists

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()


class DocumenterAgent:
    def __init__(self):
        # Embeddings + vectorstore setup
        self.vectorstore = get_vectorstore()
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 1})


        # Prompt to generate docstrings
        self.prompt = PromptTemplate.from_template("""
        You are a Python expert. Given the following function or class, generate a clean, professional docstring using triple double quotes.

        Rules:
        - Explain what it does
        - Include parameters (if any)
        - Mention return values (if applicable)
        - Be brief and accurate

        Code:
        ```python
        {code}
        ```
        """)

        self.llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        self.chain: Runnable = self.prompt | self.llm | StrOutputParser()

    def document_functions(self, code_dir: str = "data/repos", limit: int = 5):
        all_files = collect_supported_files(code_dir)
        print(f"📁 Found {len(all_files)} supported files")

        for f in all_files[:limit]:
            print(f"\n📄 File: {f}")
            blocks = parse_file_by_type(f)

            for block in blocks:
                code_snippet = block["code"]
                try:
                    docstring = self.chain.invoke({"code": code_snippet})
                    print(f"\n🔧 {block['type']} `{block['name']}` at line {block['lineno']}")
                    print(docstring.strip())
                except Exception as e:
                    print(f"❌ Failed on {block['name']}: {e}")

                    
    def summarize_file(self, filepath: str):
        """Generate a high-level summary of a Python file's purpose and structure."""
        blocks = parse_file_by_type(filepath)
        if not blocks:
            print(f"⚠️ No code blocks found in: {filepath}")
            return

        full_code = "\n\n".join([block["code"] for block in blocks])

        summary_prompt = PromptTemplate.from_template("""
        You are a senior software engineer. Given this Python file content, summarize:

        - Its purpose
        - Key classes/functions
        - Notable dependencies or imports

        File contents:
        ```python
        {code}
        ```
        """)

        chain = summary_prompt | self.llm | StrOutputParser()
        try:
            summary = chain.invoke({"code": full_code})
            print(f"\n📄 File Summary for: {filepath}")
            print(summary.strip())
        except Exception as e:
            print(f"❌ Failed to summarize file: {e}")


if __name__ == "__main__":
    print("📝 Documenter Agent Running...\n")
    agent = DocumenterAgent()

    # Function-level documentation
    agent.document_functions(limit=1)

    # File-level summary
    print("\n📘 Generating summary for a single file...\n")
    test_file = "data/repos/psf_requests/requests/sessions.py"  # Use a real one from your repo
    agent.summarize_file(test_file)

