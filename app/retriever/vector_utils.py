from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def get_vectorstore(persist_directory="chroma_db", model_name="BAAI/bge-small-en-v1.5"):
    embedding_model = HuggingFaceEmbeddings(model_name=model_name)
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
    return vectorstore
 