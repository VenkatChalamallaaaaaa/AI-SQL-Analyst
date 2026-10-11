import os, re
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from langchain_core.tools import tool
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import pandas as pd



load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])
SCHEMA_NOTES = open("schema_notes.md", encoding="utf-8").read()

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy)\b", re.I)

def is_safe(sql: str) -> bool:
    s = sql.strip().rstrip(";")
    return (s.lower().startswith(("select", "with"))
            and ";" not in s
            and not FORBIDDEN.search(s))

@tool
def get_schema() -> str:
    """Return the database schema notes: tables, columns, and what they mean."""
    return SCHEMA_NOTES

@tool
def run_sql(query: str) -> str:
    """Run ONE read-only SELECT query on the PostgreSQL database. Returns up to 50 rows."""
    if not is_safe(query):
        return "Error: only a single SELECT statement is allowed."
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            cols = list(result.keys())
            rows = [list(r) for r in result.fetchmany(50)]
        return str({"columns": cols, "rows": rows})
    except Exception as e:
        return f"SQL error: {e}"


@tool
def make_chart(query: str, chart_type: str, title: str) -> str:
    """Run ONE read-only SELECT and save a chart as a PNG.
    The query must return exactly 2 columns: x (label or date) first, y (number) second.
    chart_type must be 'line' or 'bar'. Returns the saved file path."""
    if not is_safe(query):
        return "Error: only a single SELECT statement is allowed."
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        if df.shape[1] != 2:
            return "Error: query must return exactly 2 columns (x, y)."
        os.makedirs("charts", exist_ok=True)
        path = f"charts/{abs(hash(query)) % 10**8}.png"
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x, y = df.iloc[:, 0].astype(str), df.iloc[:, 1]
        (ax.plot if chart_type == "line" else ax.bar)(x, y)
        ax.set_title(title)
        ax.set_xlabel(df.columns[0]); ax.set_ylabel(df.columns[1])
        plt.xticks(rotation=45, ha="right")
        fig.tight_layout(); fig.savefig(path); plt.close(fig)
        return f"Chart saved to {path}"
    except Exception as e:
        return f"Chart error: {e}"