import pandas as pd
import time
from datetime import datetime
from plyer import notification
import os
import winsound

# Configuration
HEART_RATE_THRESHOLD = 85
HEART_RATE_FILE = "heart_rate_data.csv"
ALERT_SOUND = "SystemExclamation"  # Windows system sound
CHECK_INTERVAL = 5  # seconds

# Track the last processed row
last_processed_index = -1

def show_alert(heart_rate, timestamp):
    """Show a desktop notification and play a sound"""
    try:
        # Play alert sound
        winsound.PlaySound(ALERT_SOUND, winsound.SND_ASYNC)
        
        # Show notification
        notification.notify(
            title="🚨 High Heart Rate Alert!",
            message=f"Heart rate is {heart_rate} BPM at {timestamp}\nThis is above the threshold of {HEART_RATE_THRESHOLD} BPM!",
            app_icon=None,
            timeout=10,
        )
        
        # Also print to console
        print(f"\n{'!'*50}")
        print(f"ALERT: High heart rate detected!")
        print(f"Time: {timestamp}")
        print(f"Heart Rate: {heart_rate} BPM")
        print(f"Threshold: {HEART_RATE_THRESHOLD} BPM")
        print(f"{'!'*50}\n")
        
    except Exception as e:
        print(f"Error showing alert: {e}")

def check_heart_rate():
    global last_processed_index
    
    try:
        # Read the CSV file
        df = pd.read_csv(HEART_RATE_FILE)
        
        # Check if there are new rows
        if len(df) <= last_processed_index:
            return
            
        # Get only new rows
        new_rows = df.iloc[last_processed_index + 1:]
        
        # Update the last processed index
        last_processed_index = len(df) - 1
        
        # Check for high heart rate in new rows
        for _, row in new_rows.iterrows():
            if pd.notna(row['BPM']) and float(row['BPM']) > HEART_RATE_THRESHOLD:
                timestamp = row['DateTime'] if 'DateTime' in row else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                show_alert(row['BPM'], timestamp)
        
    except Exception as e:
        print(f"Error checking heart rate: {e}")

def main():
    global last_processed_index
    
    # Initialize last_processed_index
    try:
        df = pd.read_csv(HEART_RATE_FILE)
        last_processed_index = len(df) - 1
        print(f"Starting heart rate monitor with threshold: {HEART_RATE_THRESHOLD} BPM")
        print(f"Monitoring file: {os.path.abspath(HEART_RATE_FILE)}")
        print("Press Ctrl+C to stop\n")
    except Exception as e:
        print(f"Error initializing: {e}")
        return
    
    # Main monitoring loop
    try:
        while True:
            check_heart_rate()
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nHeart rate monitor stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
