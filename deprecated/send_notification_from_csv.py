import pandas as pd
from datetime import datetime, timedelta
import requests
import os

def get_latest_readings(csv_file='latest_heart_rate.csv', num_readings=5):
    """Get the most recent heart rate readings from CSV file"""
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp in descending order (newest first)
        df = df.sort_values('timestamp', ascending=False)
        
        # Get the most recent readings
        latest_readings = df.head(num_readings).to_dict('records')
        
        return latest_readings
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def send_telegram_notification(readings):
    """Send notification with the latest heart rate readings"""
    if not readings:
        print("No readings to send")
        return False
    
    bot_token = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    chat_id = "6989072955"
    
    # Format the message
    message = "❤️ *LATEST HEART RATE READINGS* ❤️\n\n"
    
    # Add each reading to the message
    for i, reading in enumerate(readings, 1):
        time_str = reading['timestamp'].strftime('%I:%M %p')
        date_str = reading['timestamp'].strftime('%b %d, %Y')
        status_emoji = "⚠️" if reading['status'] == 'HIGH' else "✅"
        
        message += (
            f"{status_emoji} *Reading {i}*\n"
            f"🕒 *Time:* {time_str}\n"
            f"📅 *Date:* {date_str}\n"
            f"💓 *BPM:* {int(reading['bpm'])} ({reading['status']})\n"
        )
        
        # Add a separator if not the last reading
        if i < len(readings):
            message += "\n"
    
    # Add a note about high heart rate if any reading is high
    if any(r['status'] == 'HIGH' for r in readings):
        message += "\n⚠️ *ALERT: High heart rate detected!*\n"
        message += "Please take a moment to rest and monitor your condition.\n"
    
    message += "\n💡 *Note:* This is an automated alert. "
    message += "Contact a healthcare professional if you have concerns about your heart rate."
    
    # Send the message
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Notification sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

def main():
    print("Fetching latest heart rate readings...")
    
    # Get the 5 most recent readings
    readings = get_latest_readings(num_readings=5)
    
    if not readings:
        print("❌ No heart rate data available.")
        return
    
    print(f"Found {len(readings)} recent readings. Sending notification...")
    send_telegram_notification(readings)

if __name__ == "__main__":
    main()
