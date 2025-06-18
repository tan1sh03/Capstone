import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

# Define paths
RAW_DATA_PATH = "datasets/mouse/raw/user_mouse_movements.csv"
PROCESSED_DATA_PATH = "datasets/mouse/processed/mouse_movement_normalized.csv"

# Load dataset
df = pd.read_csv(RAW_DATA_PATH)

# Compute speed and acceleration
df["dx"] = df["x"].diff()
df["dy"] = df["y"].diff()
df["dt"] = df["timestamp"].diff()

# Avoid division by zero
df["dt"] = df["dt"].replace(0, np.nan).fillna(method="bfill")

df["speed"] = np.sqrt(df["dx"]**2 + df["dy"]**2) / df["dt"]
df["acceleration"] = df["speed"].diff() / df["dt"]

# Normalize speed and acceleration
scaler = MinMaxScaler()
df[["speed", "acceleration"]] = scaler.fit_transform(df[["speed", "acceleration"]])

# Save processed data
os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
df.to_csv(PROCESSED_DATA_PATH, index=False)

print(f"✅ Mouse movement data preprocessed and saved at: {PROCESSED_DATA_PATH}")
