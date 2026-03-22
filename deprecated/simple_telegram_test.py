import requests

def send_telegram_message(token, chat_id, message):
    """Send a message to a Telegram chat using the provided token and chat ID"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
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
            print("✅ Message sent successfully!")
            return True
        else:
            print(f"❌ Failed to send message. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

# Your credentials
BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
CHAT_ID = "6989072955"

# Test message
if __name__ == "__main__":
    print("Sending test message to Telegram...")
    send_telegram_message(
        BOT_TOKEN,
        CHAT_ID,
        "🔔 *Test Message* 🔔\nThis is a test message from your heart rate monitor."
    )
