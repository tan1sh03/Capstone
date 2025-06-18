import time
import pandas as pd
from pynput import keyboard
import os

# Constants
OUTPUT_DIR = "datasets/keystroke/raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "user_training_keystrokes.csv")
NUM_SAMPLES = 30
PASSWORD = "T4n1sh@S4snk4r"

# Ensure directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\n🎯 Type the following password 30 times **exactly as shown**:")
print("------------------------------------------------------")
print(PASSWORD)
print("------------------------------------------------------")
input("💡 Press Enter to begin typing samples...\n")

# Function to collect one password attempt
def collect_one_sample(sample_num):
    print(f"\n🔢 Sample {sample_num + 1}/{NUM_SAMPLES}")
    print("Start typing your password and press Enter when done:")

    keystroke_data = []
    pressed_keys = {}

    def on_press(key):
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            pressed_keys[key_name] = time.time()
        except:
            pass

    def on_release(key):
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            if key_name in pressed_keys:
                press_time = pressed_keys[key_name]
                release_time = time.time()
                hold_time = release_time - press_time

                if keystroke_data:
                    last_key_time = keystroke_data[-1][1]
                    flight_time = press_time - last_key_time
                else:
                    flight_time = 0

                keystroke_data.append((key_name, press_time, release_time, hold_time, flight_time))

            if key == keyboard.Key.enter:
                return False
        except:
            pass

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    return keystroke_data

# Collect 30 samples
all_keystrokes = []
for i in range(NUM_SAMPLES):
    sample = collect_one_sample(i)
    all_keystrokes.extend(sample)

# Convert to DataFrame
df_new = pd.DataFrame(all_keystrokes, columns=["key", "press_time", "release_time", "hold_time", "flight_time"])

# Append to existing dataset
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    df_final = pd.concat([df_existing, df_new], ignore_index=True)
else:
    df_final = df_new

# Save updated dataset
df_final.to_csv(OUTPUT_FILE, index=False)
print(f"\n✅ All {NUM_SAMPLES} samples collected and saved to: {OUTPUT_FILE}")
