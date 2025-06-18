import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

# Define paths
RAW_DATA_PATH = "datasets/keystroke/raw/user_training_keystrokes.csv"
PROCESSED_DATA_PATH = "datasets/keystroke/processed/keystroke_data_normalized.csv"

# Check if raw data exists
if not os.path.exists(RAW_DATA_PATH):
    raise FileNotFoundError(f"❌ File not found: {RAW_DATA_PATH}. Run keystroke collection first.")

# Load raw keystroke data
df = pd.read_csv(RAW_DATA_PATH)

# Check if raw data contains valid hold & flight time
if "key" not in df.columns or "hold_time" not in df.columns or "flight_time" not in df.columns:
    raise ValueError("❌ Error: `key`, `hold_time`, or `flight_time` columns missing. Check data collection script.")

# Mapping special key names to match model features
KEY_MAPPINGS = {
    "Key.space": "space",
    "Key.enter": "Return",
    "Key.shift": "Shift",
    "Key.caps_lock": "CapsLock",
    "Key.ctrl_l": "Ctrl",
    "Key.ctrl_r": "Ctrl",
    "Key.alt_l": "Alt",
    "Key.alt_r": "Alt",
    "Key.tab": "Tab",
    "Key.backspace": "Backspace",
    "Key.esc": "Escape",
    "Key.delete": "Delete",
    "Key.up": "Up",
    "Key.down": "Down",
    "Key.left": "Left",
    "Key.right": "Right"
}

# Convert special keys to match feature names
df["key"] = df["key"].apply(lambda k: KEY_MAPPINGS[k] if k in KEY_MAPPINGS else k)

# Extract hold time and flight time features
df_features = pd.DataFrame()

for index, row in df.iterrows():
    key = row["key"]
    hold_time = row["hold_time"]
    flight_time = row["flight_time"]

    # Feature names
    hold_feature = f"H.{key}"
    flight_feature = f"UD.{key}"

    # Assign values
    df_features.at[index, hold_feature] = hold_time
    df_features.at[index, flight_feature] = flight_time

# Fill missing values with zeros
df_features.fillna(0, inplace=True)

# Apply MinMax scaling
scaler = MinMaxScaler()
df_features[df_features.columns] = scaler.fit_transform(df_features)

# Save processed data
os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
df_features.to_csv(PROCESSED_DATA_PATH, index=False)

print(f"✅ Processed training keystroke data saved at: {PROCESSED_DATA_PATH}")
