import time
import random
import asyncio
from datetime import datetime
import pandas as pd
from telegram import Bot
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

# Heart rate thresholds (in BPM)
NORMAL_MIN = 60
NORMAL_MAX = 90
HIGH_ALERT_THRESHOLD = 100

# Initialize Telegram bot
try:
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    TELEGRAM_ENABLED = True
except Exception as e:
    logger.warning(f"Failed to initialize Telegram bot: {e}")
    TELEGRAM_ENABLED = False

# File to store heart rate data
DATA_FILE = 'heart_rate_data.csv'

# Initialize data file if it doesn't exist
try:
    pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=['timestamp', 'bpm', 'status'])
    df.to_csv(DATA_FILE, index=False)

async def send_telegram_alert(heart_rate, timestamp, is_high_alert=False):
    """Send alert to Telegram"""
    if not TELEGRAM_ENABLED:
        logger.warning("Telegram notifications are disabled")
        return False
    
    try:
        if is_high_alert:
            message = (
                "🚨 *HIGH HEART RATE ALERT!* 🚨\n\n"
                f"*Heart Rate:* `{heart_rate} BPM`\n"
                f"*Time:* `{timestamp}`\n\n"
                "⚠️ *This is significantly above normal range!*\n"
                "Please take a moment to rest and monitor your condition.\n"
                "If symptoms persist, consider seeking medical attention."
            )
        else:
            message = (
                "⚠️ *Heart Rate Alert*\n\n"
                f"*Heart Rate:* `{heart_rate} BPM`\n"
                f"*Time:* `{timestamp}`\n\n"
                "Heart rate is above normal range.\n"
                "Please take a moment to rest and relax."
            )
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        logger.info("Alert sent to Telegram")
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False

def generate_heart_rate():
    """Generate a random heart rate (simulated)"""
    # 5% chance of generating a high heart rate
    if random.random() < 0.05:
        return random.randint(100, 150)  # High heart rate
    return random.randint(60, 100)  # Normal heart rate

def log_heart_rate(heart_rate, status):
    """Log heart rate to CSV file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_data = pd.DataFrame({
            'timestamp': [timestamp],
            'bpm': [heart_rate],
            'status': [status]
        })
        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
        logger.debug(f"Logged heart rate: {heart_rate} BPM ({status})")
    except Exception as e:
        logger.error(f"Error logging heart rate: {e}")

async def monitor_heart_rate():
    """Monitor heart rate and send alerts when needed"""
    logger.info("Starting heart rate monitoring...")
    
    if TELEGRAM_ENABLED:
        try:
            me = await bot.get_me()
            logger.info(f"Connected to Telegram as @{me.username}")
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text="✅ *Heart Rate Monitor Started*\n\nMonitoring has begun. You will receive alerts for abnormal heart rates.",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send startup message to Telegram: {e}")
    
    try:
        while True:
            # Simulate getting heart rate (replace with actual sensor reading)
            heart_rate = generate_heart_rate()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Determine status
            if heart_rate > NORMAL_MAX:
                status = "HIGH"
                if heart_rate >= HIGH_ALERT_THRESHOLD:
                    status = "VERY HIGH"
                    await send_telegram_alert(heart_rate, timestamp, is_high_alert=True)
                else:
                    await send_telegram_alert(heart_rate, timestamp, is_high_alert=False)
            else:
                status = "NORMAL"
            
            # Log the reading
            log_heart_rate(heart_rate, status)
            
            # Print to console
            print(f"[{timestamp}] Heart Rate: {heart_rate} BPM - {status}")
            
            # Wait before next reading (e.g., every 5 minutes for real monitoring)
            # For demo purposes, we'll use 30 seconds
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        if TELEGRAM_ENABLED:
            try:
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text="⏹️ *Heart Rate Monitor Stopped*\n\nMonitoring has been stopped.",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send stop message to Telegram: {e}")
    except Exception as e:
        logger.error(f"Error in monitoring: {e}")
        if TELEGRAM_ENABLED:
            try:
                await bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=f"❌ *Heart Rate Monitor Error*\n\nAn error occurred: {str(e)}",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send error message to Telegram: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(monitor_heart_rate())
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Heart rate monitoring has stopped.")
