import os
import time
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"
HEART_RATE_THRESHOLD = 99  # BPM
CHECK_INTERVAL = 300  # seconds (5 minutes)

class HeartRateMonitor:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.last_notification_time = {}
        self.notification_cooldown = 3600  # 1 hour cooldown in seconds

    async def get_heart_rate_data(self):
        """Simulate getting heart rate data"""
        try:
            # For demo, generate sample data
            # In a real implementation, this would fetch from Google Fit API
            now = datetime.now()
            heart_rates = [
                {'timestamp': now - timedelta(minutes=5), 'bpm': 72},
                {'timestamp': now - timedelta(minutes=4), 'bpm': 75},
                {'timestamp': now - timedelta(minutes=3), 'bpm': 101},  # High HR for testing
                {'timestamp': now - timedelta(minutes=2), 'bpm': 78},
                {'timestamp': now - timedelta(minutes=1), 'bpm': 102},  # High HR for testing
            ]
            return pd.DataFrame(heart_rates)
        except Exception as e:
            logger.error(f"Error fetching heart rate data: {e}")
            return pd.DataFrame()

    async def send_telegram_message(self, message):
        """Send message to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='Markdown'
            )
            logger.info("Message sent to Telegram")
            return True
        except TelegramError as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def should_notify(self, bpm, timestamp):
        """Check if we should send a notification"""
        if bpm <= HEART_RATE_THRESHOLD:
            return False
            
        # Check cooldown period
        last_time = self.last_notification_time.get('high_hr', datetime.min)
        if (timestamp - last_time).total_seconds() < self.notification_cooldown:
            return False
            
        self.last_notification_time['high_hr'] = timestamp
        return True

    async def monitor_heart_rate(self):
        """Main monitoring loop"""
        await self.send_telegram_message("🚀 *Heart Rate Monitor Started*\nI'll notify you of high heart rate readings.")
        
        while True:
            try:
                # Get heart rate data
                df = await self.get_heart_rate_data()
                
                if not df.empty:
                    # Check for high heart rates
                    high_hr = df[df['bpm'] > HEART_RATE_THRESHOLD]
                    
                    for _, row in high_hr.iterrows():
                        if self.should_notify(row['bpm'], row['timestamp']):
                            message = (
                                f"⚠️ *High Heart Rate Alert!* ⚠️\n"
                                f"• *Heart Rate:* {row['bpm']} BPM\n"
                                f"• *Time:* {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                                f"• *Status:* Above {HEART_RATE_THRESHOLD} BPM"
                            )
                            await self.send_telegram_message(message)
                
                # Log current status
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"Last checked at {current_time}")
                
                # Wait for next check
                await asyncio.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

async def main():
    monitor = HeartRateMonitor()
    try:
        await monitor.monitor_heart_rate()
    except KeyboardInterrupt:
        await monitor.send_telegram_message("🛑 *Heart Rate Monitor Stopped*")
        logger.info("Monitor stopped by user")

if __name__ == "__main__":
    # Create event loop and run
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
