import pandas as pd
import matplotlib.pyplot as plt
import os

# Define paths
DATA_PATH = "datasets/mouse/processed/mouse_movement_normalized.csv"

# Load dataset
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ File not found: {DATA_PATH}. Run preprocessing first.")

df = pd.read_csv(DATA_PATH)

# Plot Mouse Speed Over Time
plt.figure(figsize=(10, 5))
plt.plot(df["timestamp"], df["speed"], label="Speed", color="blue")
plt.xlabel("Time (seconds)")
plt.ylabel("Speed (Normalized)")
plt.title("Mouse Speed Over Time")
plt.legend()
plt.show()

# Plot Mouse Acceleration Over Time
plt.figure(figsize=(10, 5))
plt.plot(df["timestamp"], df["acceleration"], label="Acceleration", color="red")
plt.xlabel("Time (seconds)")
plt.ylabel("Acceleration (Normalized)")
plt.title("Mouse Acceleration Over Time")
plt.legend()
plt.show()
