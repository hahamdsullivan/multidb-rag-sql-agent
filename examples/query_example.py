# examples/query_example.py
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from agent.sql_agent import MultiDBAgent


from router.db_router import DBRouter
from agent.sql_agent import build_agent_for_db, run_query_stream

def main():
    if len(sys.argv) < 2:
        print("Usage: python examples/query_example.py \"Your question about a DB\"")
        sys.exit(1)

    user_q = sys.argv[1]
    print("User question:", user_q)

    router = DBRouter()
    db_choice = router.route(user_q)
    if db_choice is None:
        print("Could not determine database. Try adding the DB name (e.g., 'chinook') or ensure schemas are indexed.")
        sys.exit(1)

    print("Routed to DB:", db_choice)

    agent = build_agent_for_db(db_choice)
    print("Agent built. Streaming response:\n")
    run_query_stream(agent, user_q)

if __name__ == "__main__":
    main()
