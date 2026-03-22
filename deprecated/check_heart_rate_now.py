import pandas as pd
import asyncio
from telegram import Bot
from datetime import datetime

# Telegram credentials
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

async def send_heart_rate_update():
    try:
        # Read the latest data
        df = pd.read_csv('test_heart_rate.csv')
        latest = df.iloc[-1]  # Get the most recent reading
        
        # Format the message
        message = (
            f"❤️ *Latest Heart Rate Update* ❤️\n"
            f"• *Time:* {latest['DateTime']}\n"
            f"• *Heart Rate:* {latest['BPM']} BPM\n"
            f"• *Status:* {latest['Alert']}"
        )
        
        # Send to Telegram
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        
        print("✅ Heart rate update sent to Telegram")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'bot' in locals():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(send_heart_rate_update())
    input("\nPress Enter to exit...")
