import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from models.password_gan import Generator, Discriminator, encode_password, encode_conditions, charset, INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, COND_DIM

# === Constants ===
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DATA_PATH = "C:/Users/tanis/OneDrive/Desktop/Honey-Vaults-Capstone/datasets/passwords/processed/cleaned_passwords.csv"
MODEL_PATH = "C:/Users/tanis/OneDrive/Desktop/Honey-Vaults-Capstone/models/semantic_password_gan.pth"
CHARSET_LEN = len(charset)

# === Password strength labeling ===
def get_condition_vector(password):
    return {
        "length": len(password),
        "has_upper": int(any(c.isupper() for c in password)),
        "has_digit": int(any(c.isdigit() for c in password)),
        "has_special": int(any(c in "!@#$%^&*()_+-=[]{}|;':,.<>?/`~" for c in password))
    }

# === Dataset ===
class PasswordDataset(Dataset):
    def __init__(self, passwords):
        self.data = []
        self.conditions = []
        for pwd in passwords:
            encoded_pwd = encode_password(pwd, charset)
            cond_vec = encode_conditions(get_condition_vector(pwd))

            self.data.append(torch.tensor(encoded_pwd, dtype=torch.float32))
            self.conditions.append(torch.tensor(cond_vec, dtype=torch.float32))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.conditions[idx]

# === Load Passwords ===
def load_dataset(path, max_lines=25000):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines[:max_lines]

# === Decode Function ===
def decode_password(vector):
    return ''.join([charset[int(v) % len(charset)] for v in vector])

# === Training ===
def train_conditional_gan():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Dataset not found at {DATA_PATH}")

    passwords = load_dataset(DATA_PATH)
    dataset = PasswordDataset(passwords)
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

    G = Generator(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, condition_dim=COND_DIM).to(DEVICE)
    D = Discriminator(OUTPUT_DIM, COND_DIM, HIDDEN_DIM).to(DEVICE)

    opt_G = optim.Adam(G.parameters(), lr=0.00005)     # ⬅️ Lower LR
    opt_D = optim.Adam(D.parameters(), lr=0.0002)
    loss_fn = nn.BCELoss()

    EPOCHS = 1000
    for epoch in range(EPOCHS):
        for real_pwds, conds in dataloader:
            real_pwds, conds = real_pwds.to(DEVICE), conds.to(DEVICE)
            batch_size = real_pwds.size(0)

            # === Train Discriminator ===
            z = torch.randn(batch_size, INPUT_DIM).to(DEVICE)
            fake_pwds = G(z, conds)

            real_labels = torch.ones((batch_size, 1), device=DEVICE) * 0.9         # ⬅️ Label smoothing
            fake_labels = torch.rand((batch_size, 1), device=DEVICE) * 0.1         # ⬅️ Noisy 0s

            D.zero_grad()
            real_pred = D(real_pwds, conds)
            fake_pred = D(fake_pwds.detach(), conds)

            d_loss = loss_fn(real_pred, real_labels) + loss_fn(fake_pred, fake_labels)
            d_loss.backward()
            torch.nn.utils.clip_grad_norm_(D.parameters(), 1.0)                   # ⬅️ Clip grads
            opt_D.step()

            # === Train Generator ===
            G.zero_grad()
            gen_pred = D(fake_pwds, conds)
            g_loss = loss_fn(gen_pred, real_labels)
            g_loss.backward()
            torch.nn.utils.clip_grad_norm_(G.parameters(), 1.0)                   # ⬅️ Clip grads
            opt_G.step()

        # Print progress and sample outputs
        if (epoch + 1) % 100 == 0 or epoch == 0:
            print(f"[Epoch {epoch+1}/{EPOCHS}] 🎯 D Loss: {d_loss.item():.4f} | G Loss: {g_loss.item():.4f}")

            test_z = torch.randn(5, INPUT_DIM).to(DEVICE)
            test_conds = torch.tensor([[0.6, 1, 1, 1]] * 5, dtype=torch.float32).to(DEVICE)
            test_output = G(test_z, test_conds).detach().cpu().numpy()
            decoded_samples = [decode_password((row * CHARSET_LEN).astype(int)) for row in test_output]

    # Save the generator
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    torch.save(G.state_dict(), MODEL_PATH)
    print(f"\n✅ Semantic Conditional Generator saved at: {MODEL_PATH}")

if __name__ == "__main__":
    train_conditional_gan()
