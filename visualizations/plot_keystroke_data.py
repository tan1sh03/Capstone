import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define paths
DATA_PATH = "datasets/keystroke/processed/keystroke_data_normalized.csv"

# Load dataset
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ File not found: {DATA_PATH}. Run preprocessing first.")

df = pd.read_csv(DATA_PATH)

# Plot Hold Time Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df.filter(like="H."), bins=50, kde=True, color="blue")
plt.title("Keystroke Hold Time Distribution")
plt.xlabel("Hold Time (Normalized)")
plt.ylabel("Frequency")
plt.show()

# Plot Flight Time Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df.filter(like="UD."), bins=50, kde=True, color="red")
plt.title("Keystroke Flight Time Distribution")
plt.xlabel("Flight Time (Normalized)")
plt.ylabel("Frequency")
plt.show()
