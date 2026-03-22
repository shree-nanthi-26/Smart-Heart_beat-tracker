import asyncio
from datetime import datetime
from telegram import Bot

# Configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

async def send_alert():
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        heart_rate = 98  # Sample heart rate
        status = "⚠️ High" if heart_rate > 99 else "✅ Normal"
        
        message = (
            "📊 *HEART RATE ALERT*\n\n"
            f"• *Heart Rate:* {heart_rate} BPM\n"
            f"• *Time:* {current_time}\n"
            f"• *Status:* {status}\n\n"
            "_This is a test notification with sample data._"
        )
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        print("✅ Test alert sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

if __name__ == "__main__":
    print("Sending test alert...")
    asyncio.run(send_alert())
