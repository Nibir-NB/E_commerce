import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)


def get_engine():
    """Resolves DATABASE_URL from Streamlit secrets or environment variables."""
    url = None

    try:
        import streamlit as st

        if "DATABASE_URL" in st.secrets:
            url = st.secrets["DATABASE_URL"]
    except Exception:
        pass

    if not url:
        url = os.environ.get("DATABASE_URL")

    if not url:
        raise ValueError(
            "DATABASE_URL not found! Please set it in your .env file or Streamlit secrets."
        )

    return create_engine(url, pool_pre_ping=True)


def load_customers():
    """Loads all customer records ordered by monetary value descending."""
    engine = get_engine()
    query = "SELECT * FROM customers ORDER BY monetary DESC"
    return pd.read_sql(query, engine)


def upsert_customers(df: pd.DataFrame):
    """Inserts or updates customer records in batch for high performance."""
    if df.empty:
        return

    engine = get_engine()

    records = [
        {
            "cid": str(row["customer_id"]),
            "r": float(row["Recency"]),
            "f": float(row["Frequency"]),
            "m": float(row["Monetary"]),
            "c": int(row["Cluster"]),
            "cl": str(row["cluster_label"]),
        }
        for _, row in df.iterrows()
    ]

    sql = text("""
        INSERT INTO customers (customer_id, recency, frequency, monetary, cluster, cluster_label, last_updated)
        VALUES (:cid, :r, :f, :m, :c, :cl, NOW())
        ON CONFLICT (customer_id) DO UPDATE SET
            recency = EXCLUDED.recency,
            frequency = EXCLUDED.frequency,
            monetary = EXCLUDED.monetary,
            cluster = EXCLUDED.cluster,
            cluster_label = EXCLUDED.cluster_label,
            last_updated = NOW();
    """)

    with engine.begin() as conn:
        conn.execute(sql, records)


def log_model_run(
    n_clusters: int, inertia: float, n_customers: int, accuracy: float
):
    """Logs model training metrics into the model_runs table."""
    engine = get_engine()
    sql = text("""
        INSERT INTO model_runs (n_clusters, inertia, n_customers, model_accuracy)
        VALUES (:nc, :i, :n, :a);
    """)

    with engine.begin() as conn:
        conn.execute(
            sql,
            {"nc": n_clusters, "i": inertia, "n": n_customers, "a": accuracy},
        )