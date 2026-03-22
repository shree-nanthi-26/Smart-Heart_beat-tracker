import asyncio
from telegram import Bot
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your Telegram credentials
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

async def test_connection():
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🔔 *Connection Test* 🔔\nThis is a test message from your Heart Rate Monitor.",
            parse_mode='Markdown'
        )
        print("✅ Test message sent successfully! Check your Telegram.")
        return True
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure your bot token is correct")
        print("2. Verify the chat ID is correct")
        print("3. Ensure you've started a chat with the bot")
        print("4. Check your internet connection")
        return False

if __name__ == "__main__":
    print("Testing Telegram connection...")
    asyncio.run(test_connection())
