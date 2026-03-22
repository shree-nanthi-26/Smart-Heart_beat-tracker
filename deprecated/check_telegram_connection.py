import requests

def check_telegram_connection():
    """Check if we can reach Telegram's API"""
    test_urls = [
        "https://api.telegram.org",
        "https://google.com"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing connection to {url}...")
            response = requests.get(url, timeout=10)
            print(f"✅ Success! Status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect to {url}: {e}")

if __name__ == "__main__":
    print("Testing network connections...")
    check_telegram_connection()
