# agent/sql_agent.py
import os
import re
import sqlite3
from typing import Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.schema import HumanMessage

load_dotenv()


class MultiDBAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0
        )

        self.databases: Dict[str, SQLDatabase] = {}
        self._load_databases()

    # ------------------------------------------------------------------
    # DATABASE LOADING
    # ------------------------------------------------------------------
    def _load_databases(self):
        base = os.path.join(os.getcwd(), "databases")
        for f in os.listdir(base):
            if f.endswith(".db"):
                path = os.path.join(base, f)
                uri = f"sqlite:///{path}"
                self.databases[f] = SQLDatabase.from_uri(uri)

    # ------------------------------------------------------------------
    # SAFE SCHEMA EXTRACTION (NO SAMPLE ROWS)
    # ------------------------------------------------------------------
    def _get_db_schema(self, db_name: str) -> str:
        db_path = self.databases[db_name]._engine.url.database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        schema_text = []
        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()

        for (table,) in tables:
            schema_text.append(f"Table: {table}")
            cols = cur.execute(f"PRAGMA table_info('{table}')").fetchall()
            for _, name, col_type, *_ in cols:
                schema_text.append(f"  - {name} ({col_type})")

        conn.close()
        return "\n".join(schema_text)

    def _get_all_schemas(self) -> Dict[str, str]:
        return {db: self._get_db_schema(db) for db in self.databases}

    # ------------------------------------------------------------------
    # INTENT ROUTING
    # ------------------------------------------------------------------
    def _is_db_query(self, query: str) -> bool:
        q = query.lower()
        db_keywords = [
            "show", "list", "top", "count", "average",
            "artists", "albums", "tracks",
            "orders", "invoices", "customers",
            "movies", "films", "sales"
        ]
        return any(k in q for k in db_keywords)

    def _route_db(self, query: str) -> str:
        q = query.lower()

        # 🎬 Movies / IMDb
        if any(k in q for k in ["movie", "movies", "film", "director", "actor", "rating", "popularity"]):
            return "imdb.db"

        # 🎵 Music / Chinook
        if any(k in q for k in ["artist", "album", "track", "song", "playlist", "genre"]):
            return "chinook.db"

        # 📦 Orders / Northwind
        if any(k in q for k in ["order", "orders", "ship", "customer", "supplier", "employee"]):
            return "northwind.db"

        # 🏭 Sales / AdventureWorks
        if any(k in q for k in ["product", "sales", "inventory", "price", "purchase"]):
            return "adventureworks.db"

        # ✅ Explicit DB mention still wins
        for db in self.databases:
            if db.replace(".db", "") in q:
                return db

        # ✅ Final fallback
        return "imdb.db"


    # ------------------------------------------------------------------
    # SQL GENERATION + SAFETY
    # ------------------------------------------------------------------
    def _clean_sql(self, sql: str) -> str:
        sql = re.sub(r"```sql|```", "", sql, flags=re.I)
        return sql.strip()

    def _is_safe_sql(self, sql: str) -> bool:
        banned = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
        return not any(b in sql.upper() for b in banned)

    def _generate_sql(self, query: str, db_name: str) -> str:
        schema = self._get_db_schema(db_name)

        prompt = f"""
You are an expert SQLite SQL generator.

Database schema:
{schema}

Rules:
- Output ONLY valid SQLite SQL
- No markdown
- No explanations
- Use correct table and column names only

User question:
{query}
"""
        resp = self.llm.invoke([HumanMessage(content=prompt)])
        return self._clean_sql(resp.content)

    # ------------------------------------------------------------------
    # SELF-HEALING SQL (VERY SMALL + SAFE)
    # ------------------------------------------------------------------
    def _repair_sql(self, sql: str, error: str, db_name: str) -> str:
        schema = self._get_db_schema(db_name)

        prompt = f"""
The SQL below failed.

SQL:
{sql}

Error:
{error}

Schema:
{schema}

Fix the SQL.
Rules:
- Output ONLY corrected SQL
- No explanation
"""
        resp = self.llm.invoke([HumanMessage(content=prompt)])
        return self._clean_sql(resp.content)

    # ------------------------------------------------------------------
    # MAIN ENTRY
    # ------------------------------------------------------------------
    def run_user_query(self, query: str, explicit_db: str = None) -> Any:

        # ✅ CHAT MODE (AUTO)
        if not self._is_db_query(query):
            schemas = self._get_all_schemas()
            schema_text = "\n\n".join(
                f"Database: {db}\n{schema}"
                for db, schema in schemas.items()
            )

            prompt = f"""
You have access to the following database schemas.

{schema_text}

User question:
{query}

If the answer is not in the schemas, say:
"I don’t have that information."
"""
            return self.llm.invoke(prompt).content

        # ✅ DATABASE MODE
        db_name = explicit_db or self._route_db(query)
        sql = self._generate_sql(query, db_name)

        if not self._is_safe_sql(sql):
            return "⚠️ Unsafe SQL after generation."

        try:
            rows = self.databases[db_name].run(sql)
            return {"database": db_name, "sql": sql, "rows": rows}

        except Exception as e:
            # ✅ self-healing (one retry only)
            try:
                fixed_sql = self._repair_sql(sql, str(e), db_name)
                if not self._is_safe_sql(fixed_sql):
                    return "⚠️ Unsafe SQL after repair."

                rows = self.databases[db_name].run(fixed_sql)
                return {"database": db_name, "sql": fixed_sql, "rows": rows}

            except Exception as e2:
                return f"SQL failed after self-healing: {e2}"
