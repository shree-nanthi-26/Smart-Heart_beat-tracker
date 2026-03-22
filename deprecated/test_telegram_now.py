import asyncio
from telegram import Bot
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your credentials
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

async def main():
    try:
        print("Testing Telegram connection...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Test message
        test_msg = (
            "🔔 *Test Notification* 🔔\n"
            "This is a test message from your Heart Rate Monitor.\n"
            "✅ Connection successful!"
        )
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=test_msg,
            parse_mode='Markdown'
        )
        print("✅ Test message sent successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Close the bot session
        if 'bot' in locals():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
    input("\nPress Enter to exit...")
