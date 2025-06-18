import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import os

# Define paths
DATA_PATH = "models/keystroke_anomalies.csv"

# Load dataset
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ File not found: {DATA_PATH}. Run anomaly detection first.")

df = pd.read_csv(DATA_PATH)

# Reduce features to 2D using t-SNE
X = df.drop(columns=["Anomaly"])
X_reduced = TSNE(n_components=2, perplexity=30, random_state=42).fit_transform(X)
df["x"] = X_reduced[:, 0]
df["y"] = X_reduced[:, 1]

# Plot normal vs anomalous keystrokes
plt.figure(figsize=(10, 6))
colors = {"Normal": "blue", "Anomalous": "red"}
plt.scatter(df["x"], df["y"], c=df["Anomaly"].map(colors), alpha=0.6)
plt.xlabel("t-SNE Feature 1")
plt.ylabel("t-SNE Feature 2")
plt.title("Keystroke Anomaly Detection using t-SNE")
plt.show()