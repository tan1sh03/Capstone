import os
import string
import pandas as pd
import itertools

# Define paths
RAW_DATA_PATH_1 = "datasets/passwords/raw/rockyou.txt"
RAW_DATA_PATH_2 = "datasets/passwords/raw/xato-net-10-million-passwords.txt"
CLEANED_PASSWORDS_PATH = "datasets/passwords/processed/cleaned_passwords.csv"
FEATURES_PATH = "datasets/passwords/processed/password_features.csv"

# Function to process passwords in chunks
def process_large_file(file_path, min_length=6, chunk_size=500000):
    with open(file_path, "r", encoding="latin-1") as f:
        while True:
            chunk = f.readlines(chunk_size)
            if not chunk:
                break
            yield [p.strip() for p in chunk if len(p.strip()) >= min_length]

# Function to extract password features
def password_features(passwords):
    return [
        [
            len(password),
            sum(c.isdigit() for c in password),
            sum(c.islower() for c in password),
            sum(c.isupper() for c in password),
            sum(c in string.punctuation for c in password),
        ]
        for password in passwords
    ]

# Create directories if they don’t exist
os.makedirs(os.path.dirname(CLEANED_PASSWORDS_PATH), exist_ok=True)

# Process passwords in chunks and save incrementally
with open(CLEANED_PASSWORDS_PATH, "w", encoding="utf-8") as clean_file:
    clean_file.write("password\n")  # Write header
    for chunk in itertools.chain(process_large_file(RAW_DATA_PATH_1), process_large_file(RAW_DATA_PATH_2)):
        for password in chunk:
            clean_file.write(password + "\n")  # Ensure each password is written correctly

print(f"✅ Cleaned password data saved at: {CLEANED_PASSWORDS_PATH}")

# Validate the file before reading it
with open(CLEANED_PASSWORDS_PATH, "r", encoding="utf-8") as f:
    print("🔍 First 5 lines of cleaned password file:")
    for _ in range(5):
        print(f.readline().strip())

# Process password features in chunks and save incrementally
with open(FEATURES_PATH, "w", encoding="utf-8") as feature_file:
    feature_file.write("length,digits,lowercase,uppercase,special_chars\n")  # Write header

    # Read cleaned passwords in chunks while ignoring bad lines
    chunk_iter = pd.read_csv(CLEANED_PASSWORDS_PATH, chunksize=500000, on_bad_lines='skip')

    for chunk in chunk_iter:
        if "password" not in chunk.columns:  # Ensure correct column name
            raise ValueError("❌ Column 'password' not found in cleaned password file!")

        chunk_features = password_features(chunk["password"].astype(str).tolist())

        # Convert to DataFrame and write in chunks
        df_features = pd.DataFrame(chunk_features, columns=["length", "digits", "lowercase", "uppercase", "special_chars"])
        df_features.to_csv(feature_file, index=False, header=False, mode="a")

print(f"✅ Password feature data saved at: {FEATURES_PATH}")
