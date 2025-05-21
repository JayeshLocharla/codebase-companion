import os
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.utils.parser import parse_python_file
from glob import glob
import uuid

def build_vectorstore(code_dir="data/repos", persist_dir="chroma_db"):
    # Load embedding model
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    # Setup vectorstore
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embedding_model
    )

    # Collect all parsed code blocks
    docs, metadatas = [], []
    py_files = glob(f"{code_dir}/**/*.py", recursive=True)

    for filepath in py_files:
        code_blocks = parse_python_file(filepath)
        for block in code_blocks:
            docs.append(block["code"])
            metadatas.append({
                "filename": filepath,
                "type": block["type"],
                "name": block["name"],
                "line": block["lineno"],
                "id": str(uuid.uuid4())
            })

    # Add to vectorstore
    vectorstore.add_texts(texts=docs, metadatas=metadatas)
    vectorstore.persist()
    print(f"✅ Embedded and stored {len(docs)} code blocks in Chroma.")

    return vectorstore

def test_query():
    db = Chroma(
        persist_directory="chroma_db",
        embedding_function=HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    )
    query = "How is an API call made in this repo?"
    results = db.similarity_search(query, k=3)

    for i, res in enumerate(results):
        print(f"\n🔍 Match {i+1}")
        print("📄", res.metadata["filename"])
        print("🔧", res.metadata["name"])
        print(res.page_content[:300], "...")

if __name__ == "__main__":
    build_vectorstore()
    test_query()

