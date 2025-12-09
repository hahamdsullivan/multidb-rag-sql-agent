import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loaders.db_loader import DatabaseManager

dbm = DatabaseManager()
print(dbm.list_databases())

db = dbm.load_database("chinook.db")
print(db.get_usable_table_names())
