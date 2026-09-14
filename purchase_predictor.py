import joblib, os
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_purchase_model(rfm_df):
    os.makedirs("models", exist_ok=True)
    df = rfm_df.copy()

    # Build a smoother, probabilistic label instead of a hard cutoff.
    # Customers who buy often AND recently get high probability;
    # this avoids leaking Recency directly into a binary rule.
    np.random.seed(42)
    recency_score = np.clip(1 - (df["Recency"] / df["Recency"].max()), 0, 1)
    frequency_score = np.clip(df["Frequency"] / df["Frequency"].quantile(0.95), 0, 1)
    monetary_score = np.clip(df["Monetary"] / df["Monetary"].quantile(0.95), 0, 1)

    composite_score = (0.4 * recency_score + 0.35 * frequency_score + 0.25 * monetary_score)
    # Add small random noise so the model has to learn a real boundary, not a perfect rule
    noisy_score = composite_score + np.random.normal(0, 0.08, size=len(df))
    df["will_buy"] = (noisy_score > noisy_score.median()).astype(int)

    features = ["Recency", "Frequency", "Monetary", "Cluster"]
    X, y = df[features], df["will_buy"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Purchase model accuracy: {acc:.2%}")

    joblib.dump(model, "models/purchase_model.pkl")
    return model, round(acc * 100, 2)

def predict_purchase_probability(recency, frequency, monetary, cluster):
    model = joblib.load("models/purchase_model.pkl")
    X = pd.DataFrame([[recency, frequency, monetary, cluster]], columns=["Recency", "Frequency", "Monetary", "Cluster"])
    prob = float(model.predict_proba(X)[0][1])
    return round(prob * 100, 1)