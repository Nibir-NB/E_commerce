import joblib, os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

CLUSTER_LABELS = {0: "Loyal customers", 1: "At-risk / churned", 2: "High-value whales"}

def train_and_save(rfm_df, n_clusters=3):
    os.makedirs("models", exist_ok=True)
    scaler = StandardScaler()
    X = scaler.fit_transform(rfm_df[["Recency", "Frequency", "Monetary"]])
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    model.fit(X)
    joblib.dump({"model": model, "scaler": scaler}, "models/kmeans_rfm.pkl")
    print(f"Clustering model saved. Inertia: {model.inertia_:.2f}")
    return model, scaler

def assign_clusters(rfm_df):
    artifact = joblib.load("models/kmeans_rfm.pkl")
    X = artifact["scaler"].transform(rfm_df[["Recency", "Frequency", "Monetary"]])
    rfm_df = rfm_df.copy()
    rfm_df["Cluster"] = artifact["model"].predict(X)
    rfm_df["cluster_label"] = rfm_df["Cluster"].map(CLUSTER_LABELS)
    return rfm_df

def predict_cluster(recency, frequency, monetary):
    artifact = joblib.load("models/kmeans_rfm.pkl")
    X = artifact["scaler"].transform([[recency, frequency, monetary]])
    cluster_id = int(artifact["model"].predict(X)[0])
    return cluster_id, CLUSTER_LABELS.get(cluster_id, "Unknown")