import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

def load_csv():
    engine = create_engine(os.environ["DATABASE_URL"])
    df = pd.read_csv("data/ecommerce_data.csv", encoding="latin1")
    print(f"Loaded CSV: {len(df)} rows")
    df = df.dropna(subset=["CustomerID"])
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]
    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    rows = []
    for _, r in df.iterrows():
        rows.append({"invoice_no": str(r["InvoiceNo"]), "customer_id": str(r["CustomerID"]), "description": str(r["Description"]), "quantity": int(r["Quantity"]), "invoice_date": r["InvoiceDate"], "unit_price": float(r["UnitPrice"]), "country": str(r["Country"])})
    insert_df = pd.DataFrame(rows)
    insert_df.to_sql("transactions", engine, if_exists="replace", index=False, method="multi", chunksize=500)
    print(f"Inserted {len(insert_df)} rows into transactions table")

if __name__ == "__main__":
    load_csv()