import time
import pandas as pd
from pynput import mouse
import os

# Define output file path
OUTPUT_DIR = "datasets/mouse/raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "user_mouse_movements.csv")

# Ensure directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize list to store data
mouse_data = []

# Callback function to record mouse movement
def on_move(x, y):
    timestamp = time.time()
    mouse_data.append((x, y, timestamp))

# Start listening to mouse movements
listener = mouse.Listener(on_move=on_move)
listener.start()

print("🎯 Move your mouse for 10 seconds to record data...")

# Capture movements for 10 seconds
time.sleep(10)
listener.stop()

# Convert to DataFrame
df = pd.DataFrame(mouse_data, columns=["x", "y", "timestamp"])

# Save to CSV
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Mouse movement data saved at: {OUTPUT_FILE}")
