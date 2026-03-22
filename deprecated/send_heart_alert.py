import requests
from datetime import datetime

def send_heart_alert():
    # Telegram bot configuration
    BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    CHAT_ID = "6989072955"
    
    # Heart rate details (example values - replace with actual data)
    current_bpm = 95  # Example value - replace with actual reading
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Determine alert level
    if current_bpm > 90:
        alert_level = "🚨 HIGH ALERT"
        emoji = "⚠️"
        status = "ABOVE NORMAL"
    else:
        alert_level = "ℹ️ ALERT"
        emoji = "ℹ️"
        status = "NORMAL"
    
    # Create the alert message in the requested format
    message = (
        "*HEART RATE ALERT* 🚨\n\n"
        f"*Heart Rate:* {current_bpm} BPM\n"
        f"*Date:* {current_date}\n"
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
            print("Check your Telegram for the alert message.")
        else:
            print(f"❌ Error sending alert: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("Sending heart rate alert to Telegram...")
    send_heart_alert()
    input("\nPress Enter to exit...")
