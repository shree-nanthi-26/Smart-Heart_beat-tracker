import pandas as pd
import os
from datetime import datetime
import requests

def get_latest_heart_rate():
    """Get the most recent heart rate reading from the CSV file."""
    try:
        # Try to read the latest_heart_rate.csv first
        if os.path.exists('latest_heart_rate.csv'):
            df = pd.read_csv('latest_heart_rate.csv')
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'timestamp': latest['timestamp'],
                    'bpm': int(latest['bpm']),
                    'status': latest['status']
                }
        
        # Fall back to heart_rate_data.csv if needed
        if os.path.exists('heart_rate_data.csv'):
            df = pd.read_csv('heart_rate_data.csv')
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'timestamp': latest['DateTime'],
                    'bpm': int(latest['BPM']),
                    'status': latest['Alert']
                }
        
        # If no data is found, return None
        return None
        
    except Exception as e:
        print(f"Error reading heart rate data: {e}")
        return None

def send_telegram_alert(heart_data):
    """Send a heart rate alert via Telegram."""
    BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    CHAT_ID = "6989072955"
    
    # Format the timestamp for better readability
    try:
        timestamp = datetime.strptime(heart_data['timestamp'], '%Y-%m-%d %H:%M:%S')
        formatted_time = timestamp.strftime('%B %d, %Y at %I:%M %p')
    except:
        formatted_time = heart_data['timestamp']
    
    # Determine alert level and emoji
    bpm = heart_data['bpm']
    if bpm > 90:
        alert_level = "🚨 HIGH ALERT"
        emoji = "⚠️"
        status = "ABOVE NORMAL"
    else:
        alert_level = "ℹ️ ALERT"
        emoji = "✅"
        status = "NORMAL"
    
    # Create the message
    message = (
        f"*{alert_level}: HEART RATE UPDATE* {emoji}\n\n"
        f"*Heart Rate:* {bpm} BPM\n"
        f"*Time Recorded:* {formatted_time}\n"
        f"*Status:* {status} {emoji}\n\n"
        "*Recommended Actions:*\n"
        "• Stay calm and take deep breaths\n"
        "• Sit down if you feel lightheaded\n"
        "• Drink some water\n"
        "• Contact a doctor if this persists"
    )
    
    # Send the message
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Heart rate alert sent successfully!")
            return True
        else:
            print(f"❌ Failed to send alert. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

def main():
    print("Fetching latest heart rate data...")
    heart_data = get_latest_heart_rate()
    
    if heart_data:
        print(f"Latest reading: {heart_data['bpm']} BPM ({heart_data['status']}) at {heart_data['timestamp']}")
        print("Sending alert...")
        send_telegram_alert(heart_data)
    else:
        print("❌ No heart rate data found in the CSV files.")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
