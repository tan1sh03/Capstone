import numpy as np
import pandas as pd
import joblib
import os

# Define paths
MODEL_PATH = "models/keystroke_anomaly_model.pkl"
DATA_PATH = "datasets/keystroke/processed/new_user_keystroke_normalized.csv"
TRAINED_FEATURES_PATH = "datasets/keystroke/processed/keystroke_data_normalized.csv"

# Check if files exist
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file not found: {MODEL_PATH}. Train the model first.")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ New user data not found: {DATA_PATH}. Run keystroke collection and processing first.")

if not os.path.exists(TRAINED_FEATURES_PATH):
    raise FileNotFoundError(f"❌ Feature reference file not found: {TRAINED_FEATURES_PATH}. Ensure preprocessed training data exists.")

# Load trained model
model = joblib.load(MODEL_PATH)

# Load feature names from the trained dataset
df_train = pd.read_csv(TRAINED_FEATURES_PATH)
trained_features = df_train.filter(like="H.").columns.tolist() + df_train.filter(like="UD.").columns.tolist()

# Load new user's keystroke data
df_new = pd.read_csv(DATA_PATH)

# Ensure the new dataset has the same feature columns as the trained model
for feature in trained_features:
    if feature not in df_new.columns:
        df_new[feature] = 0  # Add missing columns with default value (zero padding)

# Reorder columns to match the trained model exactly
df_new = df_new[trained_features]

# Function to classify typing session
def analyze_typing_session(df):
    anomaly_count = 0
    total_count = len(df)

    for _, row in df.iterrows():
        sample = row.tolist()
        sample_df = pd.DataFrame([sample], columns=trained_features)  # Ensure correct format
        prediction = model.predict(sample_df)  # Predict anomaly

        if prediction == -1:
            anomaly_count += 1

    # Calculate anomaly percentage
    anomaly_percentage = (anomaly_count / total_count) * 100

    # Threshold for authentication decision
    THRESHOLD = 40  # If more than 30% of keystrokes are anomalous, flag user

    print("\n📊 **Typing Session Analysis**")
    print(f"Total Keystrokes Analyzed: {total_count}")
    print(f"Anomalous Keystrokes: {anomaly_count} ({anomaly_percentage:.2f}%)")

    if anomaly_percentage > THRESHOLD:
        print("\n🚨 **Final Verdict: Anomalous Login Detected!** 🚨")
    else:
        print("\n✅ **Final Verdict: User Authenticated** ✅")

# Run anomaly detection for the entire session
analyze_typing_session(df_new)
