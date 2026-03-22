import asyncio
from datetime import datetime
from telegram import Bot

# Configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

async def send_notification():
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = (
            "🔔 *IMMEDIATE NOTIFICATION* 🔔\n\n"
            "*Heart Rate Alert*\n"
            f"• *Time:* {current_time}\n"
            "• *Status:* ⚠️ Immediate Alert\n"
            "• *Message:* This is an immediate test notification\n\n"
            "_System is operational and sending alerts._"
        )
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        print("✅ Immediate notification sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")

if __name__ == "__main__":
    print("Sending immediate notification...")
    asyncio.run(send_notification())
