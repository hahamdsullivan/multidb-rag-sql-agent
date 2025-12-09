# rag/schema_loader.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

class SchemaRAG:
    def __init__(self, persist_root="rag_store/schema_index"):
        self.persist_root = persist_root
        self.emb = OpenAIEmbeddings()
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)

    def build_schema_index(self, db_name: str, schema_text: str):
        chunks = self.splitter.split_text(schema_text)
        path = os.path.join(self.persist_root, db_name)
        os.makedirs(path, exist_ok=True)
        Chroma.from_texts(texts=chunks, embedding=self.emb, persist_directory=path)
        print(f"[ok] indexed schema -> {path}")
