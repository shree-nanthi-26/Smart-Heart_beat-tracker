import asyncio
from telegram import Bot
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Updated Telegram credentials
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

async def test_connection():
    import aiohttp
    from telegram.request import HTTPXRequest
    
    request = HTTPXRequest(connection_pool_size=1, read_timeout=30.0, write_timeout=30.0, connect_timeout=30.0)
    
    try:
        print(f"Attempting to connect with token: {TELEGRAM_BOT_TOKEN[:10]}...")
        print(f"Chat ID: {TELEGRAM_CHAT_ID}")
        
        # Test internet connection first
        print("\nChecking internet connection...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.google.com', timeout=10) as resp:
                    if resp.status == 200:
                        print("✅ Internet connection is working")
                    else:
                        print(f"⚠️ Internet connection check returned status: {resp.status}")
        except Exception as e:
            print(f"❌ Internet connection check failed: {e}")
            print("Please check your internet connection and try again.")
            return False
            
        # Test Telegram connection
        print("\nTesting Telegram API connection...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN, request=request)
        
        try:
            me = await asyncio.wait_for(bot.get_me(), timeout=30.0)
            print(f"✅ Successfully connected to Telegram API as @{me.username}")
            
            # Try sending a message
            print("\nSending test message...")
            await asyncio.wait_for(
                bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text="🔔 *Connection Successful!* 🔔\nYour heart rate monitor is now connected.",
                    parse_mode='Markdown'
                ),
                timeout=30.0
            )
            print("✅ Test message sent successfully! Check your Telegram.")
            return True
            
        except asyncio.TimeoutError:
            print("❌ Connection to Telegram API timed out.")
        except Exception as e:
            print(f"❌ Error communicating with Telegram API: {e}")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\nTroubleshooting steps:")
    print("1. Make sure your bot token is correct and hasn't been revoked")
    print("2. Verify the chat ID is correct (should be a number, not a username)")
    print("3. Ensure you've started a chat with the bot and sent it a message")
    print("4. Check if Telegram is accessible from your network (some networks block it)")
    print("5. Try using a different network (like mobile data) if on a restricted network")
    print("6. Check if the bot has the necessary permissions to send messages")
    return False

if __name__ == "__main__":
    print("Testing Telegram connection...")
    asyncio.run(test_connection())
