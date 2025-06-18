#!/usr/bin/env python3

import os
import sys
import json
import time
import base64
import hashlib
import subprocess
import pandas as pd
from pynput import keyboard

# Define paths
VAULT_PATH = "data/vault.json"
TRUTH_MAP_PATH = "data/truth_map.json"

PLAINTEXT_LIST_PATH = "data/plaintext_passwords_for_demo.txt"  # Path to the plaintext passwords
KEYSTROKE_TEMP_PATH = "datasets/keystroke/raw/new_user_keystrokes.csv"
MODEL_PATH = "models/keystroke_anomaly_model.pkl"

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs(os.path.dirname(KEYSTROKE_TEMP_PATH), exist_ok=True)

# Global variables for password collection
keystroke_data = []
pressed_keys = {}
entered_password = []

last_input_time = 0

def verify_password(entered_password):
    try:
        entered_password = entered_password.strip()

        print(f"🔍 Checking if '{entered_password}' exists in plaintext password file...")

        # Load and normalize plaintext password list
        with open(PLAINTEXT_LIST_PATH, "r", encoding="utf-8") as f:
            passwords = [line.strip() for line in f.readlines()]

        if entered_password in passwords:
            print("✅ Password found in demo list.")
            is_real = entered_password == "T4nish@s4nskar"
            return True, is_real
        else:
            print("❌ Password not found in demo list.")
            return False, False

    except Exception as e:
        print(f"❌ Error in password verification: {e}")
        return False, False

def on_press(key):
    """Callback for key press events during password entry."""
    global last_input_time
    try:
        current_time = time.time()
        key_name = key.char if hasattr(key, 'char') else str(key)
        pressed_keys[key_name] = current_time
        
        # Ignore Enter key if it's too close to the start of collection (< 300ms)
        if key == keyboard.Key.enter and (current_time - last_input_time) < 0.3:
            return
            
        # For password collection
        if key == keyboard.Key.backspace:
            if entered_password:
                entered_password.pop()
                # Update display (erase last character)
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        elif key == keyboard.Key.enter:
            # Don't add Enter to password
            pass
        elif hasattr(key, 'char'):
            entered_password.append(key.char)
            # Print asterisk for security
            sys.stdout.write('*')
            sys.stdout.flush()
            
    except Exception as e:
        pass  # Silently handle errors during keystroke collection

def on_release(key):
    """Callback for key release events during password entry."""
    try:
        key_name = key.char if hasattr(key, 'char') else str(key)
        if key_name in pressed_keys:
            press_time = pressed_keys[key_name]
            release_time = time.time()
            hold_time = release_time - press_time

            # Record flight time if there's a previous key
            if keystroke_data:
                last_key_time = keystroke_data[-1][1]  # Get press time of previous key
                flight_time = press_time - last_key_time
            else:
                flight_time = 0  # First key has no flight time

            keystroke_data.append((key_name, press_time, release_time, hold_time, flight_time))

        # Stop recording after user presses Enter
        if key == keyboard.Key.enter:
            return False
    except Exception as e:
        pass  # Silently handle errors during keystroke collection

def collect_password_with_keystrokes():
    """
    Collect password and keystroke timing data.
    Returns the entered password as a string.
    """
    global keystroke_data, entered_password, last_input_time
    keystroke_data = []  # Reset keystroke data
    entered_password = []  # Reset entered password
    
    print("\n🔒 Enter your password (press Enter when done):")
    last_input_time = time.time()  # Record when we start collecting
    
    # Start keyboard listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    
    # Save collected keystroke data to file
    df = pd.DataFrame(keystroke_data, columns=["key", "press_time", "release_time", "hold_time", "flight_time"])
    os.makedirs(os.path.dirname(KEYSTROKE_TEMP_PATH), exist_ok=True)
    df.to_csv(KEYSTROKE_TEMP_PATH, index=False)
    
    print()  # New line after password entry
    return ''.join(entered_password)  # Convert collected chars to password string

def run_script(script_path):
    """Run a Python script and return its output."""
    try:
        result = subprocess.run([sys.executable, script_path], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Script error: {e.stderr}"
    except FileNotFoundError:
        return False, f"Script not found: {script_path}"
    except Exception as e:
        return False, f"Error running script: {str(e)}"

def clear_screen():
    """Clear terminal screen for better presentation."""
    os.system('cls' if os.name == 'nt' else 'clear')

def login():
    """Main login function that integrates password and keystroke verification."""
    clear_screen()
    print("\n🔐 SECURE LOGIN SYSTEM 🔐")
    print("=========================")
    print("\nThis system authenticates users based on both:")
    print("1. Password verification")
    print("2. Keystroke dynamics analysis")
    
    # Check if necessary files exist
    if not os.path.exists(VAULT_PATH):
        print(f"❌ Error: Password vault not found at {VAULT_PATH}")
        return False
        
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Keystroke model not found at {MODEL_PATH}")
        print("⚠️ Warning: Will proceed with only password verification")
    
    # Debug: print first few entries from the vault to verify format
    try:
        with open(VAULT_PATH, "r") as f:
            vault_sample = json.load(f)[:3]
        print("\nVault Sample:")
        for i, entry in enumerate(vault_sample):
            print(f"Entry {i}: {entry}")
    except Exception as e:
        print(f"Error reading vault: {e}")
    
    # Wait for user to press Enter before starting password collection
    input("\nPress Enter to begin password entry...")
    
    # Need to add a small delay and clear the input buffer before starting password collection
    time.sleep(0.5)
    
    # For testing purposes, allow direct password input if provided
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) > 2:
            password = sys.argv[2]
            print(f"\n🔒 Test mode: Using provided password: {password}")
        else:
            password = input("\n🔒 Test mode: Enter password directly: ")
    else:
        # Collect password with keystroke timing
        password = collect_password_with_keystrokes()
    
    if not password:
        print("❌ No password entered")
        return False
    
    # Verify password
    print("\n⏳ Verifying password...")
    password_valid, is_real_password = verify_password(password)

    
    if not password_valid:
        print("❌ Invalid password")
        return False
    
    if not is_real_password:
        print("❌ Password recognized but not authorized")
        return False
    
    print("✅ Password verified")
    
    # Process keystroke data using existing script
    keystroke_valid = True  # Default to true if scripts can't run
    if os.path.exists("process_new_keystroke.py"):
        print("\n⏳ Processing keystroke data...")
        success, output = run_script("process_new_keystroke.py")
        if not success:
            print(f"❌ Failed to process keystroke data: {output}")
            print("⚠️ Continuing without keystroke verification")
        else:
            print(output)  # Display processing output
            
            # Analyze keystroke dynamics using existing script
            if os.path.exists("keystroke_real_time_detection.py"):
                print("\n⏳ Analyzing keystroke dynamics...")
                success, output = run_script("keystroke_real_time_detection.py")
                if not success:
                    print(f"❌ Failed to analyze keystroke dynamics: {output}")
                    print("⚠️ Continuing without keystroke verification")
                else:
                    print(output)  # Display analysis output
                    # Check for success indicator in output
                    keystroke_valid = "Final Verdict: User Authenticated" in output
            else:
                print("⚠️ Keystroke analysis script not found, continuing without verification")
    else:
        print("⚠️ Keystroke processing script not found, continuing without verification")
    
    # Make final authentication decision
    print("\n🔒 AUTHENTICATION RESULT 🔒")
    print("==========================")
    
    if password_valid and is_real_password:
        if keystroke_valid:
            print("\n✅ AUTHENTICATION SUCCESSFUL")
            print("Welcome to the system!")
        else:
            print("\n⚠️ PASSWORD VERIFIED BUT KEYSTROKE PATTERN SUSPICIOUS")
            print("Limited access granted - please contact administrator")
        return True
    else:
        print("\n❌ AUTHENTICATION FAILED")
        if not password_valid:
            print("Reason: Invalid password")
        elif not is_real_password:
            print("Reason: Password not authorized")
        return False

# Run the login system
if __name__ == "__main__":
    login()