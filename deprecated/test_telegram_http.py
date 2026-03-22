import requests
import json

def test_telegram_http():
    BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    CHAT_ID = "6989072955"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    try:
        # Test internet connection first
        print("Testing internet connection...")
        test_connection = requests.get("https://www.google.com", timeout=10)
        print(f"Internet connection test: {'✅ Success' if test_connection.status_code == 200 else '❌ Failed'}")
        
        # Test Telegram API
        print("\nTesting Telegram API...")
        response = requests.post(
            url,
            json={"chat_id": CHAT_ID, "text": "🔍 Testing Telegram connection..."},
            timeout=10
        )
        
        print("\nResponse Status Code:", response.status_code)
        print("Response Content:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Message sent successfully! Check your Telegram.")
        else:
            print("\n❌ Failed to send message. Response:", response.text)
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out. Could not connect to Telegram servers.")
        print("Possible causes:")
        print("1. No internet connection")
        print("2. Firewall/proxy blocking the connection")
        print("3. Telegram API is down")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_telegram_http()
