# web/fastapi_app.py

import os
import sys
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Ensure project root on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agent.sql_agent import MultiDBAgent

app = FastAPI(
    title="Multi-DB RAG SQL Agent API",
    description="Production-grade SQL agent with RAG, self-healing, cross-DB reasoning",
    version="1.0.0",
)

agent = MultiDBAgent()


# -----------------------------
# Request / Response Models
# -----------------------------

class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"
    mode: str = "db"           # "db" | "chat" | "cross"
    explicit_db: Optional[str] = None


class QueryResponse(BaseModel):
    result: object


# -----------------------------
# Routes
# -----------------------------

@app.post("/query", response_model=QueryResponse)
def query_db(req: QueryRequest):
    """
    Execute a query using the SQL agent.

    mode:
      - db    : database-backed query
      - chat  : pure LLM response
      - cross : cross-database reasoning
    """

    res = agent.run(
        query=req.query,
        session_id=req.session_id,
        mode=req.mode,
        explicit_db=req.explicit_db,
    )

    return {"result": res}


@app.get("/health")
def health():
    return {"status": "ok"}
