import pandas as pd
import asyncio
from datetime import datetime
from telegram import Bot

# Configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

def read_heart_rate_data():
    try:
        # Read the Excel file
        df = pd.read_excel('heart_rate_data.xlsx')
        
        # Get the last row (most recent reading)
        latest = df.iloc[-1].to_dict()
        
        # Format the data
        timestamp = latest.get('Timestamp', latest.get('DateTime', 'N/A'))
        heart_rate = latest.get('Heart Rate (BPM)', latest.get('BPM', 'N/A'))
        
        # Convert timestamp to readable format if it's a pandas Timestamp
        if hasattr(timestamp, 'strftime'):
            timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'timestamp': timestamp,
            'heart_rate': heart_rate,
            'status': '⚠️ High' if isinstance(heart_rate, (int, float)) and heart_rate > 99 else '✅ Normal'
        }
        
    except Exception as e:
        print(f"Error reading data: {e}")
        return None

async def send_telegram_alert(data):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        message = (
            "💓 *HEART RATE UPDATE*\n\n"
            f"• *Heart Rate:* `{data['heart_rate']}` BPM\n"
            f"• *Time:* `{data['timestamp']}`\n"
            f"• *Status:* {data['status']}\n\n"
            "_This is the latest reading from your heart rate monitor._"
        )
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        print("✅ Alert notification sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")

async def main():
    print("Fetching latest heart rate data...")
    heart_data = read_heart_rate_data()
    
    if heart_data:
        print(f"Latest reading: {heart_data['heart_rate']} BPM at {heart_data['timestamp']}")
        await send_telegram_alert(heart_data)
    else:
        # Send an error notification if data couldn't be read
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text="❌ *ERROR*\nCould not read heart rate data. Please check the Excel file.",
                parse_mode='Markdown'
            )
            print("❌ Error notification sent")
        except Exception as e:
            print(f"Failed to send error notification: {e}")

if __name__ == "__main__":
    asyncio.run(main())
