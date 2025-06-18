import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
import joblib
import os

# Define paths
DATA_PATH = "datasets/keystroke/processed/keystroke_data_normalized.csv"
MODEL_PATH = "models/keystroke_anomaly_model.pkl"

# Load dataset
df = pd.read_csv(DATA_PATH)

# Select keystroke timing features (H. and UD. columns)
features = df.filter(like="H.").columns.tolist() + df.filter(like="UD.").columns.tolist()
X = df[features]

# Split into training and testing sets
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

# Train Isolation Forest for anomaly detection
model = IsolationForest(n_estimators=100, contamination=0.10, random_state=42)
model.fit(X_train)

# Save trained model
os.makedirs("models", exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"✅ Keystroke anomaly detection model saved at: {MODEL_PATH}")

# Predict anomalies on test data
predictions = model.predict(X_test)

# Convert results (-1 means anomaly, 1 means normal)
df_results = X_test.copy()
df_results["Anomaly"] = predictions
df_results["Anomaly"] = df_results["Anomaly"].apply(lambda x: "Anomalous" if x == -1 else "Normal")

# Save results
df_results.to_csv("models/keystroke_anomalies.csv", index=False)
print("✅ Keystroke anomaly detection results saved.")

