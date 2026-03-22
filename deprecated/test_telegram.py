import os
from dotenv import load_dotenv
from telegram_bot import TelegramBot
import asyncio

async def test_telegram_bot():
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Error: Missing Telegram bot token or chat ID in .env file")
        return
    
    # Initialize the bot
    bot = TelegramBot(token=token, chat_id=chat_id)
    
    # Send a test message
    print("Sending test message to Telegram...")
    success = await bot.send_alert(
        heart_rate=120,  # Test heart rate
        timestamp="2023-10-01 15:30:00"  # Test timestamp
    )
    
    if success:
        print("✅ Test message sent successfully! Check your Telegram.")
    else:
        print("❌ Failed to send test message. Check your internet connection and bot settings.")

if __name__ == "__main__":
    asyncio.run(test_telegram_bot())
