import pandas as pd
import requests
from datetime import datetime

def analyze_heart_rate():
    try:
        # Read the Excel file
        df = pd.read_excel('heart_rate_data.xlsx')
        
        # Get the latest reading
        latest = df.iloc[-1]
        
        # Get basic statistics
        avg_bpm = df['BPM'].mean()
        max_bpm = df['BPM'].max()
        min_bpm = df['BPM'].min()
        
        # Check for high heart rate
        threshold = 85
        high_readings = df[df['BPM'] > threshold]
        
        return {
            'latest_bpm': latest['BPM'],
            'timestamp': f"{latest['Date']} {latest['Time']}",
            'avg_bpm': round(avg_bpm, 1),
            'max_bpm': max_bpm,
            'min_bpm': min_bpm,
            'above_threshold': len(high_readings),
            'total_readings': len(df)
        }
        
    except Exception as e:
        print(f"Error analyzing data: {e}")
        return None

def send_telegram_alert(stats):
    bot_token = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    chat_id = "6989072955"
    threshold = 85  # BPM threshold for alerts
    
    # Format the message with emojis
    message = (
        "📊 *Heart Rate Analysis* 📊\n\n"
        f"❤️ *Latest Reading:* {stats['latest_bpm']} BPM\n"
        f"🕒 *Time:* {stats['timestamp']}\n\n"
        "📈 *Statistics*\n"
        f"• Average: {stats['avg_bpm']} BPM\n"
        f"• Highest: {stats['max_bpm']} BPM\n"
        f"• Lowest: {stats['min_bpm']} BPM\n\n"
        f"⚠️ *Alerts:* {stats['above_threshold']} readings above {threshold} BPM\n"
        f"📋 *Total Readings:* {stats['total_readings']}"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Heart rate analysis sent to Telegram!")
        else:
            print(f"❌ Error sending alert: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    print("Analyzing heart rate data...")
    
    # Get heart rate statistics
    stats = analyze_heart_rate()
    
    if stats:
        print(f"Latest reading: {stats['latest_bpm']} BPM")
        print(f"Average BPM: {stats['avg_bpm']}")
        print(f"Readings above threshold: {stats['above_threshold']}/{stats['total_readings']}")
        
        # Send the analysis to Telegram
        print("\nSending analysis to Telegram...")
        send_telegram_alert(stats)
    else:
        print("Could not analyze heart rate data.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
