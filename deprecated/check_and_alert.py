import pandas as pd
import os
from datetime import datetime
import requests

def get_latest_heart_rate():
    """Get the latest heart rate reading from the log file"""
    log_file = "heart_rate_data.csv"
    
    if not os.path.exists(log_file):
        print("No heart rate data found. The monitor may not have collected any data yet.")
        return None, None
    
    try:
        # Read the CSV file
        df = pd.read_csv(log_file)
        
        # Convert timestamp to datetime if needed
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            latest = df.iloc[-1]  # Get the most recent entry
            return latest['bpm'], latest['timestamp']
            
    except Exception as e:
        print(f"Error reading heart rate data: {e}")
    
    return None, None

def send_telegram_alert(heart_rate, timestamp):
    """Send a heart rate alert to Telegram"""
    bot_token = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    chat_id = "6989072955"
    
    alert_message = (
        "🚨 *HEART RATE ALERT* 🚨\n\n"
        f"*Current Heart Rate:* {heart_rate:.0f} BPM\n"
        f"*Time:* {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        "*Status:* ABOVE THRESHOLD (88 BPM)\n\n"
        "ℹ️ This is an automated alert. "
        "Consider checking your vitals if this persists."
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": alert_message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Alert sent successfully!")
            return True
        else:
            print(f"❌ Error sending alert: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    print("Checking latest heart rate...")
    
    # Get the latest heart rate
    bpm, timestamp = get_latest_heart_rate()
    
    if bpm is not None:
        print(f"Latest reading: {bpm:.0f} BPM at {timestamp}")
        
        # Check if heart rate is above threshold
        if bpm > 88:
            print(f"Heart rate is above threshold (88 BPM). Sending alert...")
            send_telegram_alert(bpm, timestamp)
        else:
            print(f"Heart rate is normal (≤ 88 BPM). No alert needed.")
    else:
        print("Could not retrieve heart rate data.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
