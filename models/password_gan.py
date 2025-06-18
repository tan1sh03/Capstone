import torch
import torch.nn as nn

charset = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:',.<>?/")  # 90 chars
charset_LEN = len(charset)
MAX_LEN = 12  # fixed password length
INPUT_DIM = 100
HIDDEN_DIM = 256
OUTPUT_DIM = MAX_LEN  # number of characters
COND_DIM = 4  # length, has_upper, has_digit, has_special

def encode_password(password, charset):
    encoded = [charset.index(c) if c in charset else 0 for c in password[:MAX_LEN]]
    while len(encoded) < MAX_LEN:
        encoded.append(0)
    return encoded

def decode_password(indices):
    return ''.join([charset[i % charset_LEN] for i in indices])

def encode_conditions(password):
    return [
        min(len(password), 20) / 20.0,
        float(any(c.isupper() for c in password)),
        float(any(c.isdigit() for c in password)),
        float(any(c in "!@#$%^&*()_+-=[]{}|;:',.<>?/" for c in password))
    ]

class Generator(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, condition_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim + condition_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
            nn.Sigmoid()
        )

    def forward(self, z, conds):
        x = torch.cat((z, conds), dim=1)
        return self.fc(x)

class Discriminator(nn.Module):
    def __init__(self, input_dim, condition_dim, hidden_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim + condition_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, x, conds):
        x = torch.cat((x, conds), dim=1)
        return self.fc(x)
