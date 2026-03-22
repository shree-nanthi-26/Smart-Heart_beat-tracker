import asyncio
from telegram import Bot
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your credentials
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

async def send_test_message():
    try:
        print("Initializing bot...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Test the connection
        me = await bot.get_me()
        print(f"✅ Connected to bot: @{me.username}")
        
        # Send test message
        test_message = (
            "🔔 *Test Message from SmartHeartBeat* 🔔\n\n"
            "This is a test notification to verify that the Telegram bot is working correctly.\n"
            "If you can see this message, the bot is properly configured! 🎉"
        )
        
        print("Sending test message...")
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=test_message,
            parse_mode='Markdown'
        )
        print("✅ Test message sent successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if your bot token is correct")
        print("2. Make sure the chat ID is correct")
        print("3. Check your internet connection")
        print("4. Make sure you've started a chat with the bot")
        print("5. Ensure the bot has permission to send you messages")

if __name__ == "__main__":
    asyncio.run(send_test_message())
