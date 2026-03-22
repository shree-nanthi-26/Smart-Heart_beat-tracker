import pandas as pd
from datetime import datetime, timedelta
import requests
import os

def get_heart_rate_summary():
    """Get the latest heart rate reading and summary statistics"""
    try:
        # Read the CSV file
        df = pd.read_csv('latest_heart_rate.csv')
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp (newest first)
        df = df.sort_values('timestamp', ascending=False)
        
        # Get the most recent reading
        latest = df.iloc[0].to_dict()
        
        # Calculate summary statistics
        total_readings = len(df)
        high_readings = len(df[df['status'] == 'HIGH'])
        high_percent = (high_readings / total_readings) * 100
        avg_bpm = df['bpm'].mean()
        
        # Get readings from the last 24 hours
        one_day_ago = datetime.now() - timedelta(days=1)
        recent_readings = df[df['timestamp'] > one_day_ago]
        
        summary = {
            'latest': {
                'bpm': int(latest['bpm']),
                'status': latest['status'],
                'timestamp': latest['timestamp']
            },
            'stats': {
                'total_readings': total_readings,
                'high_readings': high_readings,
                'high_percent': round(high_percent, 1),
                'avg_bpm': round(avg_bpm, 1),
                'recent_count': len(recent_readings)
            },
            'last_5': df.head(5).to_dict('records')
        }
        
        return summary
        
    except Exception as e:
        print(f"Error processing heart rate data: {e}")
        return None

def send_heart_rate_alert():
    """Send a heart rate alert with latest reading and summary"""
    # Get the heart rate data
    data = get_heart_rate_summary()
    if not data:
        print("❌ Could not retrieve heart rate data")
        return False
    
    latest = data['latest']
    stats = data['stats']
    
    # Format the message
    message = "❤️ *HEART RATE ALERT* ❤️\n\n"
    
    # Add latest reading
    time_str = latest['timestamp'].strftime('%I:%M %p')
    date_str = latest['timestamp'].strftime('%A, %B %d, %Y')
    status_emoji = "⚠️" if latest['status'] == 'HIGH' else "✅"
    
    message += (
        f"{status_emoji} *Latest Reading*\n"
        f"🕒 {time_str} • {date_str}\n"
        f"💓 *{latest['bpm']} BPM* ({latest['status']})\n\n"
    )
    
    # Add summary statistics
    message += (
        "📊 *Summary*\n"
        f"• Average BPM: {stats['avg_bpm']}\n"
        f"• High readings: {stats['high_readings']}/{stats['total_readings']} ({stats['high_percent']}%)\n"
        f"• Last 24h: {stats['recent_count']} readings\n\n"
    )
    
    # Add recent readings
    message += "⏱ *Recent Readings*\n"
    for reading in data['last_5']:
        time = reading['timestamp'].strftime('%I:%M %p')
        status_emoji = "⚠️" if reading['status'] == 'HIGH' else "•"
        message += f"{status_emoji} {time}: {int(reading['bpm'])} BPM\n"
    
    # Add alert if heart rate is high
    if latest['status'] == 'HIGH':
        message += "\n🚨 *ALERT: High heart rate detected!*\n"
        message += "Please take a moment to rest and monitor your condition.\n"
    
    message += "\n💡 *Note:* This is an automated alert. "
    message += "Contact a healthcare professional if you have concerns about your heart rate."
    
    # Send the message
    try:
        bot_token = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
        chat_id = "6989072955"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Heart rate alert sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending alert: {e}")
        return False

if __name__ == "__main__":
    print("Sending heart rate alert...")
    send_heart_rate_alert()
