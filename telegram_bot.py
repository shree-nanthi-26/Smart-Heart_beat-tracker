from telegram import Bot
from telegram.error import TelegramError
import logging
import asyncio

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        """
        Initialize the Telegram bot.
        
        Args:
            token (str): Your Telegram bot token from BotFather
            chat_id (str): The chat ID where messages will be sent
        """
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=self.token)
    
    async def send_alert(self, heart_rate: int, timestamp: str) -> bool:
        """
        Send a heart rate alert to Telegram.
        
        Args:
            heart_rate (int): The heart rate in BPM
            timestamp (str): The timestamp of the reading
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        try:
            message = (
                f"🚨 *High Heart Rate Alert!* 🚨\n\n"
                f"• *Heart Rate:* `{heart_rate} BPM`\n"
                f"• *Time:* `{timestamp}`\n\n"
                "_This is above the normal range. Please check your vitals._"
            )
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"Telegram alert sent for heart rate: {heart_rate} BPM")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

# Example usage
async def example_usage():
    # Replace these with your actual bot token and chat ID
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"
    
    # Initialize the bot
    bot = TelegramBot(token=BOT_TOKEN, chat_id=CHAT_ID)
    
    # Send a test alert
    success = await bot.send_alert(
        heart_rate=120,
        timestamp="2023-10-01 14:30:00"
    )
    
    if success:
        print("Test alert sent successfully!")
    else:
        print("Failed to send test alert.")

if __name__ == "__main__":
    asyncio.run(example_usage())
