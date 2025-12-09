# router/db_router.py
from loaders.db_loader import DatabaseManager
from rag.retriever import SchemaRetriever

class DBRouter:
    def __init__(self):
        self.dbm = DatabaseManager()
        self.retriever = SchemaRetriever()

    def route(self, query: str):
        # explicit mention
        q = query.lower()
        for db in self.dbm.list_databases():
            if db.split(".")[0].lower() in q:
                return db
        # keyword mapping
        keyword_map = {
            "order": ["northwind.db", "chinook.db"],
            "invoice": ["chinook.db"],
            "movie": ["imdb.db"]
        }
        for k, dbs in keyword_map.items():
            if k in q:
                return dbs[0]
        # fallback to RAG similarity
        dbs = self.dbm.list_databases()
        best = self.retriever.best_match_db(query, dbs)
        return best if best else (dbs[0] if dbs else None)
