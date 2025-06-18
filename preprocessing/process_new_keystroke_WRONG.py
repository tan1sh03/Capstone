import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

# Define paths
RAW_DATA_PATH = "datasets/keystroke/raw/new_user_keystrokes_WRONG.csv"
PROCESSED_DATA_PATH = "datasets/keystroke/processed/new_user_keystroke_normalized_WRONG.csv"
TRAINED_FEATURES_PATH = "datasets/keystroke/processed/keystroke_data_normalized.csv"

# Check if raw data exists
if not os.path.exists(RAW_DATA_PATH):
    raise FileNotFoundError(f"❌ File not found: {RAW_DATA_PATH}. Run keystroke collection first.")

# Check if training feature reference exists
if not os.path.exists(TRAINED_FEATURES_PATH):
    raise FileNotFoundError(f"❌ Feature reference file not found: {TRAINED_FEATURES_PATH}. Ensure preprocessed training data exists.")

# Load training feature reference
df_train = pd.read_csv(TRAINED_FEATURES_PATH)
trained_features = df_train.filter(like="H.").columns.tolist() + df_train.filter(like="UD.").columns.tolist()

# Load new user's keystroke data
df_new = pd.read_csv(RAW_DATA_PATH)

# Check if raw data contains valid hold & flight time
if "key" not in df_new.columns or "hold_time" not in df_new.columns or "flight_time" not in df_new.columns:
    raise ValueError("❌ Error: `key`, `hold_time`, or `flight_time` columns missing in new_user_keystrokes.csv. Check data collection script.")

# Mapping special key names to match trained feature names
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
df_new["key"] = df_new["key"].apply(lambda k: KEY_MAPPINGS[k] if k in KEY_MAPPINGS else k)

# Debugging: Print the first 10 keys being processed
print("\n🔍 First 10 keystroke entries being mapped:")
print(df_new[["key", "hold_time", "flight_time"]].head(10))

# Initialize DataFrame with correct feature columns
df_new_features = pd.DataFrame(0, index=np.arange(len(df_new)), columns=trained_features)

# Assign `hold_time` and `flight_time` values to the correct columns
for index, row in df_new.iterrows():
    key = row["key"]
    hold_time = row["hold_time"]
    flight_time = row["flight_time"]

    # Construct feature names
    hold_feature = f"H.{key}"
    flight_feature = f"UD.{key}"

    # Debugging: Check feature mappings
    if hold_feature not in trained_features:
        print(f"⚠️ Warning: {hold_feature} not found in trained dataset.")
    if flight_feature not in trained_features:
        print(f"⚠️ Warning: {flight_feature} not found in trained dataset.")

    # Assign values only if the feature exists in trained dataset
    if hold_feature in df_new_features.columns:
        df_new_features.at[index, hold_feature] = hold_time
    if flight_feature in df_new_features.columns:
        df_new_features.at[index, flight_feature] = flight_time

# Fill missing values with zeros (for unseen keys)
df_new_features.fillna(0, inplace=True)

# Debugging: Check extracted feature values before normalization
print("\n🔍 Checking extracted features before normalization:")
print(df_new_features.head())

# Apply the same MinMax scaling as the training data
if df_new_features[trained_features].sum().sum() == 0:
    print("⚠️ Warning: Feature values are all zero before normalization! Skipping scaling.")
else:
    scaler = MinMaxScaler()
    scaler.fit(df_train[trained_features])  # Use the same training scaler
    df_new_features[trained_features] = scaler.transform(df_new_features[trained_features])

# Save processed data
os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
df_new_features.to_csv(PROCESSED_DATA_PATH, index=False)

print(f"✅ Processed new user keystroke data saved at: {PROCESSED_DATA_PATH}")
