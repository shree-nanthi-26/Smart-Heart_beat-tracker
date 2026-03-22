import asyncio
from telegram import Bot

async def test_telegram():
    BOT_TOKEN = "8168004449:AAHsY9KsZN2ZGU3EeEVlV5sAXwdGXpal_ss"
    CHAT_ID = "7332916002"
    
    try:
        print("Initializing bot...")
        bot = Bot(token=BOT_TOKEN)
        print("Sending test message...")
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🚀 Test message from SmartHeartBeat!"
        )
        print("✅ Test message sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Telegram test...")
    success = asyncio.run(test_telegram())
    if success:
        print("✅ Telegram bot is working correctly!")
    else:
        print("❌ Could not send Telegram message. Please check your bot token and chat ID.")
