import pandas as pd
import asyncio
from telegram import Bot
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram configuration (using your existing credentials)
TELEGRAM_BOT_TOKEN = "8168004449:AAHsY9KsZN2ZGU3EeEVlV5sAXwdGXpal_ss"
TELEGRAM_CHAT_ID = "7332916002"

# Heart rate threshold (in BPM)
HEART_RATE_THRESHOLD = 85

# File to monitor
HEART_RATE_FILE = "heart_rate_data.csv"

# Track the last processed row to avoid duplicate alerts
last_processed_index = -1

async def send_telegram_alert(heart_rate, timestamp):
    """Send alert to Telegram"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        message = (
            f"🚨 *HEART RATE ALERT* 🚨\n"
            f"• *Time:* {timestamp}\n"
            f"• *Heart Rate:* {heart_rate} BPM\n"
            f"• *Status:* ABOVE THRESHOLD ({HEART_RATE_THRESHOLD} BPM)"
        )
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Alert sent for heart rate: {heart_rate} BPM")
    except Exception as e:
        logger.error(f"Error sending Telegram alert: {e}")

def check_heart_rate():
    global last_processed_index
    
    try:
        # Read the CSV file
        df = pd.read_csv(HEART_RATE_FILE)
        
        # Check if there are new rows
        if len(df) <= last_processed_index:
            return False
            
        # Get only new rows
        new_rows = df.iloc[last_processed_index + 1:]
        
        # Update the last processed index
        last_processed_index = len(df) - 1
        
        # Check for high heart rate in new rows
        for _, row in new_rows.iterrows():
            if pd.notna(row['BPM']) and float(row['BPM']) > HEART_RATE_THRESHOLD:
                return {
                    'heart_rate': row['BPM'],
                    'timestamp': row['DateTime'] if 'DateTime' in row else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'HIGH'
                }
        return False
        
    except Exception as e:
        logger.error(f"Error checking heart rate: {e}")
        return False

async def main():
    global last_processed_index
    
    # Initialize last_processed_index
    try:
        df = pd.read_csv(HEART_RATE_FILE)
        last_processed_index = len(df) - 1
        logger.info(f"Starting to monitor {HEART_RATE_FILE}")
        logger.info(f"Initial heart rate threshold: {HEART_RATE_THRESHOLD} BPM")
    except Exception as e:
        logger.error(f"Error initializing: {e}")
        return
    
    # Main monitoring loop
    while True:
        try:
            alert = check_heart_rate()
            if alert:
                await send_telegram_alert(alert['heart_rate'], alert['timestamp'])
            
            # Check every 5 seconds
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(10)  # Wait longer if there's an error

if __name__ == "__main__":
    print(f"Starting heart rate monitor with threshold: {HEART_RATE_THRESHOLD} BPM")
    print(f"Monitoring file: {HEART_RATE_FILE}")
    print("Press Ctrl+C to stop")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nHeart rate monitor stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")
