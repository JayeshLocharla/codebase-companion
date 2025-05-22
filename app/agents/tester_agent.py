import os
from dotenv import load_dotenv
from glob import glob

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from app.utils.file_utils import collect_supported_files
from app.utils.parser import parse_file_by_type

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class TesterAgent:
    def __init__(self):
        self.prompt = PromptTemplate.from_template("""
        You are a Python testing expert.
        Given a function or class, write a unit test in `pytest` style.

        Guidelines:
        - Use realistic inputs and edge cases
        - Focus on correctness and coverage
        - Add mock data if needed
        - Only return the test function, no explanations

        Code to test:
        ```python
        {code}
        ```
        """)

        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
        self.chain: Runnable = self.prompt | self.llm | StrOutputParser()

    def generate_tests(self, code_dir="data/repos", max_files=3):
        all_files = collect_supported_files(code_dir)
        print(f"🧪 Found {len(all_files)} supported files")

        for f in all_files[:max_files]:
            print(f"\n📂 Testing file: {f}")
            blocks = parse_file_by_type(f)

            for block in blocks:
                try:
                    test_code = self.chain.invoke({"code": block["code"]})
                    print(f"\n🧪 Test for {block['type']} `{block['name']}` at line {block['lineno']}:\n")
                    print(test_code.strip())
                except Exception as e:
                    print(f"❌ Failed to generate test for `{block['name']}`: {e}")

if __name__ == "__main__":
    print("🧪 Tester Agent Running...\n")
    agent = TesterAgent()
    agent.generate_tests(max_files=2)
