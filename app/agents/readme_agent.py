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


class ReadmeAgent:
    def __init__(self):
        self.prompt = PromptTemplate.from_template("""
        You are a senior software engineer and technical writer.
        Given this codebase context, write a professional-level README.md draft.

        Include:
        - Project title and purpose
        - Key modules and features
        - How to install and run
        - Example usage
        - Testing and contribution instructions

        Be concise, clear, and helpful for new developers.

        Codebase summary:
        ```python
        {code}
        ```
        """)

        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        self.chain: Runnable = self.prompt | self.llm | StrOutputParser()

    def generate_readme(self, code_dir="data/repos", max_blocks=50):
        py_files = glob(f"{code_dir}/**/*.py", recursive=True)
        print(f"📁 Found {len(py_files)} Python files in repo")

        all_blocks = []
        for f in py_files:
            blocks = parse_python_file(f)
            all_blocks.extend(block["code"] for block in blocks)

        if not all_blocks:
            return "⚠️ No code blocks found to generate README."

        # Limit total tokens (simple block count cap)
        full_context = "\n\n".join(all_blocks[:max_blocks])
        print(f"🧠 Using {min(max_blocks, len(all_blocks))} code blocks for README generation...")

        try:
            return self.chain.invoke({"code": full_context}).strip()
        except Exception as e:
            return f"❌ Failed to generate README: {e}"


if __name__ == "__main__":
    agent = ReadmeAgent()
    print("📄 Generating Full README Draft...\n")
    readme = agent.generate_readme()
    print(readme)
