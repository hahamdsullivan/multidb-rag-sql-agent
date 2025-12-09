# web/streamlit_app.py
import os
import sys
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agent.sql_agent import MultiDBAgent

st.set_page_config(page_title="Multi-DB RAG SQL Agent", layout="wide")

agent = MultiDBAgent()

def render_rows(rows, sql=None, agent=None, db_name=None):
    if rows is None:
        st.info("No rows returned.")
        return

    if not isinstance(rows, list):
        st.write(rows)
        return

    if len(rows) == 0:
        st.info("No rows returned.")
        return

    # ✅ If SQL + agent + DB available → infer column names
    if sql and agent and db_name:
        try:
            db = agent.databases[db_name]
            with db._engine.connect() as conn:
                result = conn.execute(sql)
                columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df, use_container_width=True)
            return
        except Exception:
            pass  # fallback below

    # ✅ Fallback: generic columns
    cols = [f"col_{i}" for i in range(len(rows[0]))]
    df = pd.DataFrame(rows, columns=cols)
    st.dataframe(df, use_container_width=True)




st.title("🧠 Multi-DB RAG SQL Agent")

db_names = ["auto"] + list(agent.databases.keys())
explicit_db = st.selectbox("Database", db_names)
if explicit_db == "auto":
    explicit_db = None

#session_id = st.text_input("Session ID", value="default")
query = st.text_area("Ask your question")

if st.button("Run Query") and query.strip():
    with st.spinner("Thinking..."):
        res = agent.run_user_query(
                query=query,
                explicit_db=explicit_db
            )

        if isinstance(res, dict):
            st.subheader(f"Database: {res['database']}")
            st.code(res["sql"], language="sql")
            render_rows(
                        res["rows"],
                        sql=res["sql"],
                        agent=agent,
                        db_name=res["database"]
                    )

        else:
            st.write(res)
