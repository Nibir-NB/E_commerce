import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from sqlalchemy import create_engine

def compute_rfm():
    engine = create_engine(os.environ["DATABASE_URL"])
    df = pd.read_sql("SELECT customer_id, invoice_date, quantity * unit_price AS revenue FROM transactions", engine)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    snapshot = df["invoice_date"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("customer_id").agg(Recency=("invoice_date", lambda x: (snapshot - x.max()).days), Frequency=("invoice_date", "count"), Monetary=("revenue", "sum")).reset_index()
    rfm = rfm[rfm["Monetary"] > 0].copy()
    print(f"RFM computed for {len(rfm)} customers")
    return rfm