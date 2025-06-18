import hashlib
import os
import base64
import random

PEPPER_PATH = "data/pepper.secret"

# Only generate a new pepper if one doesn't exist
if not os.path.exists(PEPPER_PATH):
    os.makedirs(os.path.dirname(PEPPER_PATH), exist_ok=True)
    with open(PEPPER_PATH, "wb") as f:
        f.write(os.urandom(16))
    print("✅ New pepper generated and saved.")

with open(PEPPER_PATH, "rb") as f:
    PEPPER = f.read()

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    elif isinstance(salt, str):
        try:
            salt = base64.b64decode(salt)
        except:
            salt = salt.encode()
    pwd_peppered = password.encode() + PEPPER
    hashed = hashlib.pbkdf2_hmac("sha256", pwd_peppered, salt, 100_000)
    return {
        "salt": base64.b64encode(salt).decode(),
        "hash": base64.b64encode(hashed).decode()
    }