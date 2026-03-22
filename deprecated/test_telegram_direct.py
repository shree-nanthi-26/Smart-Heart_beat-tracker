import requests
import json

# Your credentials
BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
CHAT_ID = "6989072955"

# Test message
test_message = "🔔 Direct API Test - Please ignore"

# URL for sending message
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Request data
payload = {
    'chat_id': CHAT_ID,
    'text': test_message,
    'parse_mode': 'HTML'
}

print(f"Testing connection to Telegram API...")
print(f"Bot Token: {BOT_TOKEN[:10]}...")
print(f"Chat ID: {CHAT_ID}")

try:
    # Make the request
    response = requests.post(url, data=payload, timeout=10)
    
    # Print the response
    print("\nResponse Status Code:", response.status_code)
    print("Response Content:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ Message sent successfully! Check your Telegram.")
    else:
        print("\n❌ Failed to send message. Response:", response.text)
        
        # Common issues
        if response.status_code == 401:
            print("\n⚠️  Error: Unauthorized. Check your bot token.")
        elif response.status_code == 400:
            print("\n⚠️  Error: Bad Request. Check your chat ID.")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Error making request: {e}")
    print("\nPossible issues:")
    print("1. No internet connection")
    print("2. Telegram API is blocked in your region")
    print("3. Bot token is invalid or revoked")
    print("4. Chat ID is incorrect")
    
    # Test internet connection
    try:
        test_connection = requests.get("https://api.telegram.org", timeout=5)
        print("\n✅ Internet connection to Telegram API is working")
    except:
        print("\n❌ Cannot connect to Telegram API. Check your internet connection or if Telegram is blocked in your network.")
