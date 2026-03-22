import asyncio
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
from telegram import Bot

# Configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"
SCOPES = ["https://www.googleapis.com/auth/fitness.heart_rate.read"]

async def get_recent_heart_rate():
    """Fetch recent heart rate data from Google Fit."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        print("Please run google_fit_heart.py first to authenticate")
        return None

    try:
        service = build('fitness', 'v1', credentials=creds)
        now = datetime.utcnow()
        start_time = (now - timedelta(minutes=60)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        end_time = now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
        dataset_id = f"{start_time}-{end_time}"
        
        data = service.users().dataSources().datasets() \
            .get(userId='me', dataSourceId=data_source, datasetId=dataset_id) \
            .execute()
            
        return data.get('point', [])
    except Exception as e:
        print(f"Error fetching heart rate data: {e}")
        return None

async def send_telegram_notification(message):
    """Send a notification via Telegram."""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        print("Notification sent successfully!")
    except Exception as e:
        print(f"Failed to send notification: {e}")

async def main():
    print("Fetching recent heart rate data...")
    heart_rate_data = await get_recent_heart_rate()
    
    if not heart_rate_data:
        message = "❌ No recent heart rate data available or error fetching data."
        print(message)
    else:
        latest_reading = heart_rate_data[-1] if heart_rate_data else None
        if latest_reading:
            heart_rate = latest_reading['value'][0]['fpVal']
            timestamp = latest_reading['startTimeNanos']
            timestamp = datetime.fromtimestamp(int(timestamp) / 1e9).strftime('%Y-%m-%d %H:%M:%S')
            
            message = (
                f"💓 *Latest Heart Rate Reading*\n"
                f"• *Rate:* {heart_rate:.0f} BPM\n"
                f"• *Time:* {timestamp}\n"
                f"• *Status:* {'⚠️ High' if heart_rate > 99 else '✅ Normal'}"
            )
            print(f"Latest reading: {heart_rate:.0f} BPM at {timestamp}")
        else:
            message = "ℹ️ No recent heart rate readings available."
    
    # Send the notification
    await send_telegram_notification(message)

if __name__ == "__main__":
    asyncio.run(main())
