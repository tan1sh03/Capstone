import os
import json
import base64
import random
import re
from hasher import hash_password  # Uses external pepper from hasher.py

# Paths
REAL_PASSWORD_PATH = "data/real_password.txt"
VAULT_PATH = "data/vault.json"               # Public-facing vault
TRUTH_MAP_PATH = "data/truth_map.json"       # Secure server-side truth file
PLAINTEXT_LIST_PATH = "data/plaintext_passwords_for_demo.txt"  # For demo purposes

# Bi-directional substitutions (chars → symbols and digits → chars)
SUBSTITUTIONS = {
    'a': ['4', '@'], '4': ['a'],
    'i': ['1', '!', '|'], '1': ['i', 'l'],
    'e': ['3'], '3': ['e'],
    'o': ['0'], '0': ['o'],
    's': ['$', '5'], '5': ['s'],
    'l': ['1'], '|': ['l'], 
    't': ['7', '+'], '7': ['t'],
    'b': ['8'], '8': ['b'],
    'g': ['9', '6'], '9': ['g'], '6': ['g'],
    'z': ['2'], '2': ['z'],
    'h': ['#'], '#': ['h'],
}

PREFIXES = ["", "secure", "my", "password", "secret", "pass"]
SUFFIXES = ["", "123", "2024", "2023", "!", "1!", "?", "!!!", "123!"]
SEPARATORS = [".", "@", "_", "-", ""]

def reverse_substitution(word):
    """Apply reverse substitutions (numbers/symbols → letters)."""
    reversed_word = ""
    for char in word:
        if char in SUBSTITUTIONS:
            if random.random() < 0.3:
                reversed_word += random.choice(SUBSTITUTIONS[char])
            else:
                reversed_word += char
        else:
            reversed_word += char
    return reversed_word

def basic_mutations(password, count=30):
    """Generates character-substituted mutations of a password."""
    variants = set()
    variants.add(password)

    for _ in range(count):
        mutated = []
        for c in password:
            if c in SUBSTITUTIONS and random.random() < 0.5:
                mutated.append(random.choice(SUBSTITUTIONS[c]))
            else:
                mutated.append(c)
        variants.add(''.join(mutated))

    return list(variants)

def word_variations(password):
    """Generate word-based separator mutations and reordering."""
    variants = set()
    variants.add(password)

    for sep in SEPARATORS:
        if sep and sep in password:
            parts = password.split(sep)
            if len(parts) >= 2:
                for i in range(len(parts)):
                    reordered = parts[i:] + parts[:i]
                    variants.add(sep.join(reordered))

                for new_sep in SEPARATORS:
                    if new_sep != sep:
                        variants.add(new_sep.join(parts))

    return list(variants)

def add_affixes(passwords):
    """Add common prefixes and suffixes."""
    variants = set(passwords)
    
    # Store original passwords to track them
    original_pwd_map = {pwd: pwd for pwd in passwords}
    
    for pwd in list(passwords):
        for pre in PREFIXES:
            for suf in SUFFIXES:
                if pre or suf:
                    new_pwd = f"{pre}{pwd}{suf}"
                    variants.add(new_pwd)
                    # Remember where this variant came from
                    original_pwd_map[new_pwd] = pwd
    
    return list(variants), original_pwd_map

def generate_password_variants(real_password, target_count=100):
    all_variants = set()
    all_variants.add(real_password)
    all_variants.update(word_variations(real_password))
    
    # Keep track of variants derived from real_password
    derived_from_real = set([real_password])
    for variant in word_variations(real_password):
        derived_from_real.add(variant)
    
    sub_variants = set()
    for variant in list(all_variants):
        new_variants = set(basic_mutations(variant, 5))
        new_variants.add(reverse_substitution(variant))
        sub_variants.update(new_variants)
        
        # Track which came from real password
        if variant in derived_from_real:
            derived_from_real.update(new_variants)
    
    all_variants.update(sub_variants)
    
    # Apply affixes while tracking origins
    final_variants, origin_map = add_affixes(all_variants)
    final_variants = list(set(final_variants))
    
    # Update derived_from_real with the affixed variants
    for variant, origin in origin_map.items():
        if origin in derived_from_real:
            derived_from_real.add(variant)
    
    # Ensure real password is included
    if real_password not in final_variants:
        final_variants.append(real_password)
    
    random.shuffle(final_variants)
    
    # Limit to target count but ensure real password is included
    result = final_variants[:target_count]
    if real_password not in result:
        replace_idx = random.randint(0, len(result) - 1)
        result[replace_idx] = real_password
    
    # Return both the variants and the set of those derived from real password
    return result, derived_from_real

# === Load and process real password ===
with open(REAL_PASSWORD_PATH, "r", encoding="utf-8") as f:
    real_password = f.read().strip()

all_passwords, derived_from_real = generate_password_variants(real_password, target_count=200)

# === Create vault, truth map, plaintext demo ===
vault = []
truth_map = {}
plaintext_demo_list = []

for pwd in all_passwords:
    hashed = hash_password(pwd)
    vault.append({
        "hash": hashed["hash"],
        "salt": hashed["salt"]
    })
    
    # Set the truth value correctly - only the exact real password is True
    truth_map[hashed["hash"]] = (pwd == real_password)
    
    plaintext_demo_list.append(pwd)

# === Save files ===
os.makedirs("data", exist_ok=True)

with open(VAULT_PATH, "w") as f:
    json.dump(vault, f, indent=2)

with open(TRUTH_MAP_PATH, "w") as f:
    json.dump(truth_map, f, indent=2)

with open(PLAINTEXT_LIST_PATH, "w", encoding="utf-8") as f:
    for pwd in plaintext_demo_list:
        f.write(pwd + "\n")

print(f"✅ Vault saved to: {VAULT_PATH}")
print(f"✅ Truth map saved to: {TRUTH_MAP_PATH} (secure)")
print(f"✅ Plaintext password demo saved to: {PLAINTEXT_LIST_PATH}")
print(f"Real password: {real_password}")
print(f"Real password in list: {real_password in plaintext_demo_list}")
print(f"Number of passwords derived from real: {len([p for p in plaintext_demo_list if p in derived_from_real])}")