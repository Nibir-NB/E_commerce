import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()
from scripts.rfm_engine import compute_rfm
from clustering import train_and_save, assign_clusters
from purchase_predictor import train_purchase_model
from db import upsert_customers, log_model_run

def run():
    print("Step 1: Compute RFM")
    rfm = compute_rfm()
    print("Step 2: Train clustering model")
    model, scaler = train_and_save(rfm)
    print("Step 3: Assign clusters")
    rfm = assign_clusters(rfm)
    print("Step 4: Train purchase predictor")
    _, accuracy = train_purchase_model(rfm)
    print("Step 5: Write to database")
    upsert_customers(rfm)
    print("Step 6: Log run")
    log_model_run(3, round(model.inertia_, 2), len(rfm), accuracy)
    print("Pipeline complete!")

if __name__ == "__main__":
    run()