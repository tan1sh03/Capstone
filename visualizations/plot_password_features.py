import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os

# Define paths
DATA_PATH = "datasets/passwords/processed/password_features.csv"
CLEANED_PATH = "datasets/passwords/processed/cleaned_passwords.csv"

# Load dataset
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ File not found: {DATA_PATH}. Run preprocessing first.")

df = pd.read_csv(DATA_PATH)

# Plot Password Length Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["length"], bins=30, kde=True, color="green")
plt.title("Password Length Distribution")
plt.xlabel("Password Length")
plt.ylabel("Frequency")
plt.show()

# Plot Character Composition
fig, ax = plt.subplots(2, 2, figsize=(12, 10))

sns.histplot(df["digits"], bins=20, kde=True, ax=ax[0, 0], color="blue")
ax[0, 0].set_title("Digits in Passwords")

sns.histplot(df["lowercase"], bins=20, kde=True, ax=ax[0, 1], color="red")
ax[0, 1].set_title("Lowercase Characters in Passwords")

sns.histplot(df["uppercase"], bins=20, kde=True, ax=ax[1, 0], color="purple")
ax[1, 0].set_title("Uppercase Characters in Passwords")

sns.histplot(df["special_chars"], bins=20, kde=True, ax=ax[1, 1], color="orange")
ax[1, 1].set_title("Special Characters in Passwords")

plt.tight_layout()
plt.show()

# Generate Word Cloud if cleaned passwords are available
if os.path.exists(CLEANED_PATH):
    df_cleaned = pd.read_csv(CLEANED_PATH)
    wordcloud = WordCloud(width=800, height=400, background_color="black").generate(" ".join(df_cleaned["password"]))

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Common Passwords Word Cloud")
    plt.show()
