import asyncio
from telegram import Bot

async def test_telegram():
    # Using the latest bot token and chat ID
    BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    CHAT_ID = "6989072955"
    
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🚀 Test message from SmartHeartBeat!"
        )
        print("✅ Test message sent successfully!")
    except Exception as e:
        print(f"❌ Error sending message: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram())
