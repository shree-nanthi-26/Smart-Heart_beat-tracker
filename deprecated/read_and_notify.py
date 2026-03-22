import pandas as pd
import asyncio
from datetime import datetime
from telegram import Bot

# Configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"
EXCEL_FILE = "heart_rate_data.xlsx"

def get_latest_reading():
    try:
        # Read the Excel file
        df = pd.read_excel(EXCEL_FILE)
        
        # Get the last row (most recent reading)
        latest = df.iloc[-1]
        
        # Extract relevant data
        data = {
            'date': latest.get('Date', 'N/A'),
            'timestamp': latest.get('Timestamp', 'N/A'),
            'heart_rate': latest.get('Heart Rate (BPM)', 'N/A'),
            'status': latest.get('Status', 'N/A')
        }
        
        return data, None
        
    except Exception as e:
        return None, f"Error reading data: {str(e)}"

async def send_alert(data, error=None):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        if error:
            message = f"❌ *Error*\n{error}"
        else:
            # Format the message
            message = (
                "📊 *LATEST HEART RATE READING*\n\n"
                f"• *Date:* {data.get('date', 'N/A')}\n"
                f"• *Time:* {data.get('timestamp', 'N/A')}\n"
                f"• *Heart Rate:* {data.get('heart_rate', 'N/A')} BPM\n"
                f"• *Status:* {data.get('status', 'N/A')}\n\n"
                "_Data retrieved from heart_rate_data.xlsx_"
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
    print("Reading latest data and sending notification...")
    data, error = get_latest_reading()
    
    if error:
        print(f"Error: {error}")
    else:
        print(f"Latest reading: {data}")
    
    await send_alert(data, error)

if __name__ == "__main__":
    asyncio.run(main())
