import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys
from send_heart_alert import send_heart_alert

def get_latest_heart_rate():
    """Get the most recent heart rate from the CSV file."""
    try:
        # Check both possible CSV files
        csv_files = ['heart_rate_data.csv', 'latest_heart_rate.csv']
        latest_data = None
        
        for file in csv_files:
            if os.path.exists(file):
                df = pd.read_csv(file)
                if not df.empty:
                    # Get the most recent record
                    if 'timestamp' in df.columns and 'bpm' in df.columns:
                        latest = df.iloc[-1]
                        latest_data = {
                            'bpm': int(latest['bpm']),
                            'timestamp': latest['timestamp'],
                            'status': latest.get('status', 'NORMAL')
                        }
                    elif 'DateTime' in df.columns and 'BPM' in df.columns:
                        latest = df.iloc[-1]
                        latest_data = {
                            'bpm': int(latest['BPM']),
                            'timestamp': latest['DateTime'],
                            'status': latest.get('Alert', 'NORMAL')
                        }
                    break
        
        return latest_data
        
    except Exception as e:
        print(f"Error reading heart rate data: {e}")
        return None

def format_heart_rate_display(heart_data):
    """Format the heart rate data for display."""
    if not heart_data:
        return "No heart rate data available."
    
    bpm = heart_data['bpm']
    timestamp = heart_data['timestamp']
    status = heart_data['status']
    
    # Add emoji based on status
    if 'HIGH' in status:
        status_emoji = "⚠️"
    else:
        status_emoji = "✅"
    
    return (
        f"🫀 *LATEST HEART RATE*\n"
        f"\n"
        f"📊 *{bpm} BPM* {status_emoji}\n"
        f"⏰ {timestamp}\n"
        f"📊 Status: {status}\n"
        f"\n"
    )

def check_and_alert(heart_data):
    """Check if alert needs to be sent and send it."""
    if not heart_data:
        return
    
    bpm = heart_data['bpm']
    timestamp = heart_data['timestamp']
    
    # Check if alert is needed
    if bpm > 90:  # Threshold for high heart rate
        print(f"⚠️  High heart rate detected: {bpm} BPM")
        
        # Send alert using the existing function
        try:
            send_heart_alert()
            print("✅ Alert sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
    else:
        print("✅ Heart rate is within normal range")

def main():
    print("❤️  Heart Rate Monitor - Live View")
    print("=" * 40)
    
    try:
        while True:
            # Clear the console (works in most terminals)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Get and display the latest heart rate
            heart_data = get_latest_heart_rate()
            
            if heart_data:
                print(format_heart_rate_display(heart_data))
                check_and_alert(heart_data)
            else:
                print("No heart rate data found. Waiting for data...")
            
            # Wait before next update
            print("\n" + "=" * 40)
            print("Press Ctrl+C to exit")
            print("Refreshing in 10 seconds...")
            
            # Wait for 10 seconds or until interrupted
            try:
                for _ in range(10):
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
