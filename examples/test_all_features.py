# examples/test_all_features.py
import sys
import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from agent.sql_agent import MultiDBAgent

agent = MultiDBAgent()

tests = [
    "In Chinook, show the top 5 artists by number of tracks",
    "Which tables store orders and what are the order date columns?",
    "Show the top 5 movies",
    "Do you know who is haham?"
]

for q in tests:
    print("\nQUERY:", q)
    res = agent.run_user_query(q)
    print(res)
