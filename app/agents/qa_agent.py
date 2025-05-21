import os
from dotenv import load_dotenv
from glob import glob

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from app.utils.parser import parse_python_file

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class QAAgent:
    def __init__(self):
        self.prompt = PromptTemplate.from_template("""
        You are a senior software engineer performing a code quality review.
        Review the following Python code and provide feedback on:

        - Code readability and structure
        - Naming conventions (functions, variables)
        - Potential bugs or logic errors
        - Style and formatting (PEP8)
        - Suggestions for modularity and maintainability

        Be concise, professional, and list your feedback in bullet points.

        Code:
        ```python
        {code}
        ```
        """)

        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
        self.chain: Runnable = self.prompt | self.llm | StrOutputParser()

    def review_codebase(self, code_dir="data/repos", max_files=3):
        py_files = glob(f"{code_dir}/**/*.py", recursive=True)
        print(f"📁 Found {len(py_files)} Python files")

        for f in py_files[:max_files]:
            print(f"\n📄 Reviewing: {f}")
            blocks = parse_python_file(f)

            for block in blocks:
                try:
                    review = self.chain.invoke({"code": block["code"]})
                    print(f"\n🔍 {block['type']} `{block['name']}` at line {block['lineno']}")
                    print(review.strip())
                except Exception as e:
                    print(f"❌ Failed to review `{block['name']}`: {e}")


if __name__ == "__main__":
    print("🧪 QA Agent Starting...\n")
    agent = QAAgent()
    agent.review_codebase(max_files=2)
