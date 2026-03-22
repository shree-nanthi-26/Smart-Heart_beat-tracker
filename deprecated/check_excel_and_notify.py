import pandas as pd
import asyncio
from datetime import datetime
from telegram import Bot
import os

# Configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"
EXCEL_FILE = "heart_rate_data.xlsx"

def read_latest_heart_rate():
    """Read the latest heart rate from the Excel file."""
    try:
        if not os.path.exists(EXCEL_FILE):
            return None, None, "Excel file not found"
        
        df = pd.read_excel(EXCEL_FILE)
        if df.empty:
            return None, None, "Excel file is empty"
            
        # Get the latest record (assuming there's a timestamp column)
        latest = df.iloc[-1]
        return latest['Heart Rate (BPM)'], latest['Timestamp'], None
        
    except Exception as e:
        return None, None, f"Error reading Excel file: {str(e)}"

async def send_telegram_notification(heart_rate, timestamp, error_msg=None):
    """Send a notification via Telegram."""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        if error_msg:
            message = f"❌ *Error*\n{error_msg}"
        else:
            # Format the timestamp if it's a datetime object
            if isinstance(timestamp, (pd.Timestamp, datetime)):
                timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            status = "⚠️ High" if heart_rate > 99 else "✅ Normal"
            
            message = (
                "📊 *Latest Heart Rate Reading*\n\n"
                f"• *Heart Rate:* {heart_rate} BPM\n"
                f"• *Time:* {timestamp}\n"
                f"• *Status:* {status}\n\n"
                "_Data retrieved from local Excel file._"
            )
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        print("✅ Notification sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")

async def main():
    print(f"Reading data from {EXCEL_FILE}...")
    heart_rate, timestamp, error = read_latest_heart_rate()
    
    if error:
        print(f"Error: {error}")
    else:
        print(f"Latest reading: {heart_rate} BPM at {timestamp}")
    
    await send_telegram_notification(heart_rate, timestamp, error)

if __name__ == "__main__":
    asyncio.run(main())
