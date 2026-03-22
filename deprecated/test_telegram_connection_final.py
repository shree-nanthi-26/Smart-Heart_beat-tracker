import asyncio
from telegram import Bot
import logging

# Configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_telegram_connection():
    """Test Telegram bot connection and send a test message"""
    try:
        # Initialize bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Test connection
        me = await bot.get_me()
        logger.info(f"Connected to bot: @{me.username} ({me.first_name})")
        
        # Send test message
        message = await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="✅ *Heart Rate Monitor is now active!*\n\n"
                 "I'll notify you if your heart rate goes above 90 BPM.\n"
                 "_Monitoring will start in a moment..._",
            parse_mode='Markdown'
        )
        
        logger.info(f"Test message sent to chat {TELEGRAM_CHAT_ID}")
        return True
        
    except Exception as e:
        logger.error(f"Telegram connection failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing Telegram connection...")
    success = asyncio.run(test_telegram_connection())
    
    if success:
        logger.info("✅ Telegram test successful! Starting main monitor...")
        # Import and run the main monitor
        import telegram_heart_monitor
    else:
        logger.error("❌ Telegram test failed. Please check your token and chat ID.")
