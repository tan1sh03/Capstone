import os
import torch
import numpy as np
from models.password_gan import Generator, decode_password, encode_conditions, INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, COND_DIM, charset

MODEL_PATH = "models/semantic_password_gan.pth"
OUTPUT_PATH = "datasets/passwords/generated_semantic_honeytokens.txt"

generator = Generator(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, COND_DIM)
generator.load_state_dict(torch.load(MODEL_PATH))
generator.eval()

def generate_honeytokens(n=10, conditions=None):
    if conditions is None:
        conditions = [{
            "length": 10, "has_upper": 1, "has_digit": 1, "has_special": 1
        }] * n

    z = torch.randn(n, INPUT_DIM)
    cond_vecs = torch.tensor([encode_conditions(c) for c in conditions], dtype=torch.float32)
    outputs = generator(z, cond_vecs).detach().numpy()
    rounded = np.rint(outputs * len(charset)).clip(0, len(charset)-1).astype(int)
    passwords = [decode_password(row) for row in rounded]
    return passwords

# Example usage
example_conditions = [
    {"length": 12, "has_upper": 1, "has_digit": 1, "has_special": 1},
    {"length": 10, "has_upper": 0, "has_digit": 1, "has_special": 0},
    {"length": 8,  "has_upper": 1, "has_digit": 0, "has_special": 0},
    {"length": 9,  "has_upper": 1, "has_digit": 1, "has_special": 1},
    {"length": 11, "has_upper": 0, "has_digit": 1, "has_special": 1},
    {"length": 7,  "has_upper": 0, "has_digit": 0, "has_special": 0},
    {"length": 13, "has_upper": 1, "has_digit": 1, "has_special": 1},
    {"length": 12, "has_upper": 1, "has_digit": 1, "has_special": 0},
    {"length": 10, "has_upper": 1, "has_digit": 1, "has_special": 1},
    {"length": 14, "has_upper": 1, "has_digit": 1, "has_special": 1},
]

tokens = generate_honeytokens(10, example_conditions)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    f.write('\n'.join(tokens))

print("✅ Generated Honeytokens:\n", tokens)
