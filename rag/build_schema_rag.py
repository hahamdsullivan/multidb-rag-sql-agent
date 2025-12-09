import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Allow project-wide imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from loaders.db_loader import DatabaseManager
from rag.schema_loader import SchemaRAG

dbm = DatabaseManager()
rag = SchemaRAG()

print("\n🔍 Building schema RAG index...\n")

for db_name in dbm.list_databases():
    print(f"[BUILD] Extracting schema for: {db_name}")

    db = dbm.load_database(db_name)
    schema_text = db.get_table_info()

    rag.build_schema_index(db_name, schema_text)

print("\n🎉 DONE — All schemas indexed!")
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Allow project-wide imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from loaders.db_loader import DatabaseManager
from rag.schema_loader import SchemaRAG

dbm = DatabaseManager()
rag = SchemaRAG()

print("\n🔍 Building schema RAG index...\n")

for db_name in dbm.list_databases():
    print(f"[BUILD] Extracting schema for: {db_name}")

    db = dbm.load_database(db_name)
    schema_text = db.get_table_info()

    rag.build_schema_index(db_name, schema_text)

print("\n🎉 DONE — All schemas indexed!")
