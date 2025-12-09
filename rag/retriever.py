# rag/retriever.py
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

ROOT = os.path.dirname(os.path.dirname(__file__))
SCHEMA_INDEX_ROOT = os.path.join(ROOT, "rag_store", "schema_index")

class SchemaRetriever:
    def __init__(self, index_root=SCHEMA_INDEX_ROOT):
        self.index_root = index_root
        self.emb = OpenAIEmbeddings()

    def _index_path(self, db_name):
        return os.path.join(self.index_root, db_name)

    def load_retriever(self, db_name, k=5):
        path = self._index_path(db_name)
        vect = Chroma(persist_directory=path, embedding_function=self.emb)
        return vect.as_retriever(search_kwargs={"k": k})

    def best_match_db(self, query, db_list):
        best_db = None
        best_score = -1e9
        for db in db_list:
            path = self._index_path(db)
            if not os.path.exists(path):
                continue
            vect = Chroma(persist_directory=path, embedding_function=self.emb)
            res = vect.similarity_search_with_score(query, k=1)
            if res:
                score = res[0][1]
                if score > best_score:
                    best_score = score
                    best_db = db
        return best_db
