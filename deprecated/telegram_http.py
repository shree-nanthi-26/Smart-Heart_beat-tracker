import requests

def send_telegram_message():
    bot_token = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    chat_id = "6989072955"
    
    message = "🔔 *Heart Rate Alert* 🔔\n" \
              "This is a test message using HTTP.\n" \
              "If you see this, the connection is working!"
    
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
            print("✅ Message sent successfully!")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Try disabling VPN or proxy")
        print("3. Check if Telegram API is accessible in your region")
        print("4. Verify your bot token and chat ID")

if __name__ == "__main__":
    print("Sending test message to Telegram...")
    send_telegram_message()
    input("\nPress Enter to exit...")
