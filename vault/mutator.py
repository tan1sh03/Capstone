import random
import string

LEET_MAP = {'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'], 's': ['$', '5'], 't': ['7']}
COMMON_SUFFIXES = ['1', '!', '123', '2024', '007', '!!', '@', 'password']
CASE_FLIPS = [str.upper, str.lower, lambda c: c]

def realistic_mutations(password, count=20):
    variants = set()

    while len(variants) < count:
        pwd = list(password)

        # 1. Leetspeak swaps
        for i, char in enumerate(pwd):
            if char.lower() in LEET_MAP and random.random() < 0.3:
                pwd[i] = random.choice(LEET_MAP[char.lower()])

        # 2. Case changes
        pwd = [random.choice(CASE_FLIPS)(c) if c.isalpha() else c for c in pwd]

        # 3. Add suffix or prefix
        if random.random() < 0.5:
            pwd.append(random.choice(COMMON_SUFFIXES))
        else:
            pwd.insert(0, random.choice(COMMON_SUFFIXES))

        variants.add(''.join(pwd))

    return list(variants)
