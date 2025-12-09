# loader/db_loader.py
import os
from langchain_community.utilities import SQLDatabase


class PatchedSQLDatabase(SQLDatabase):
    """SQLDatabase with patched get_table_info signature compatible with LangChain tools."""

    def get_table_info(self, table_names=None):
        """
        Accepts None, string, comma-separated string, or list.
        Safely quotes names with spaces before running PRAGMA.
        """
        # No tables specified → ALL tables
        if table_names is None:
            tables = self.get_usable_table_names()
        elif isinstance(table_names, str):
            tables = [t.strip() for t in table_names.split(",")]
        else:
            tables = table_names

        result_parts = []
        for table in tables:
            try:
                # quote table names that contain spaces or special characters
                if " " in table or "-" in table or table.lower() != table:
                    table_quoted = f'"{table}"'
                else:
                    table_quoted = table

                rows = self.run(f"PRAGMA table_info({table_quoted});")
                col_lines = "\n".join([f"- {r[1]} ({r[2]})" for r in rows])
                result_parts.append(f"Table: {table}\nColumns:\n{col_lines}\n")
            except Exception as e:
                result_parts.append(f"Table: {table}\nError: {e}\n")
        return "\n".join(result_parts)


class DatabaseManager:
    """Loads .db files from databases/ folder using PatchedSQLDatabase."""

    def __init__(self, base_path="databases"):
        self.base_path = base_path

    def list_databases(self):
        return [f for f in os.listdir(self.base_path) if f.endswith(".db")]

    def load_database(self, db_name: str):
        db_path = os.path.join(self.base_path, db_name)
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found: {db_path}")
        uri = f"sqlite:///{db_path}"
        return PatchedSQLDatabase.from_uri(uri)
