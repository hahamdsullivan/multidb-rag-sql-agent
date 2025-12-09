# examples/test_self_healing.py
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# ensure project root on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agent.sql_agent import MultiDBAgent

def pretty_print_result(res):
    if isinstance(res, dict):
        print("Routed DB:", res["database"])
        print("Executed SQL:\n", res["sql_query"])
        print("Result:\n", res["result"])
    else:
        print("Agent Response:", res)

if __name__ == "__main__":
    agent = MultiDBAgent(openai_model="gpt-4o-mini", db_path="databases")

    q1 = "In Chinook, show the top 5 artists by number of tracks"
    res1 = agent.run_user_query(q1, explicit_db="chinook.db")
    print("\n=== Query 1 ===")
    pretty_print_result(res1)

    q2 = "Which tables store orders and what are the order date columns?"
    res2 = agent.run_user_query(q2, explicit_db="northwind.db")
    print("\n=== Query 2 ===")
    pretty_print_result(res2)

    q3 = "DROP TABLE Customers;"
    res3 = agent.run_user_query(q3, explicit_db="northwind.db")
    print("\n=== Query 3 ===")
    pretty_print_result(res3)
