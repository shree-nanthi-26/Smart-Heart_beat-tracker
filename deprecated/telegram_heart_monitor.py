import os
import time
import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load configuration
try:
    from config import (
        SCOPES,
        CLIENT_SECRET_FILE,
        TOKEN_FILE,
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
        HEART_RATE_THRESHOLD,
        CHECK_INTERVAL,
        LOG_FILE,
        LOG_LEVEL
    )
    
    class Config:
        # Google Fit API
        SCOPES = SCOPES
        CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
        TOKEN_FILE = TOKEN_FILE
        
        # Telegram Configuration
        TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
        TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID
        
        # Heart Rate Settings
        HEART_RATE_THRESHOLD = HEART_RATE_THRESHOLD
        CHECK_INTERVAL = CHECK_INTERVAL
        
        # Logging
        LOG_FILE = LOG_FILE
        LOG_LEVEL = getattr(logging, LOG_LEVEL, logging.INFO)

except ImportError:
    raise ImportError(
        "Please create a config.py file with your configuration. "
        "You can use config_example.py as a template."
    )

# Set up logging
def setup_logging():
    logging.basicConfig(
        level=Config.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Initialize Telegram bot
try:
    telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
    logger.info("Telegram bot initialized successfully")
    TELEGRAM_ENABLED = True
except Exception as e:
    logger.error(f"Failed to initialize Telegram bot: {e}")
    TELEGRAM_ENABLED = False

async def send_telegram_alert(heart_rate: float, timestamp: datetime):
    """Send heart rate alert to Telegram"""
    if not TELEGRAM_ENABLED:
        logger.warning("Telegram notifications are disabled")
        return False
    
    try:
        message = (
            f"🚨 *HIGH HEART RATE ALERT!* 🚨\n\n"
            f"• *Heart Rate:* `{heart_rate:.0f} BPM`\n"
            f"• *Time:* `{timestamp.strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            "_This is above the normal range. Please check your vitals._"
        )
        
        await telegram_bot.send_message(
            chat_id=Config.TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Telegram alert sent for heart rate: {heart_rate} BPM")
        return True
    except TelegramError as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Telegram alert: {e}")
        return False

def authenticate():
    """Authenticate with Google Fit API"""
    creds = None
    
    # Check for existing token
    if os.path.exists(Config.TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(Config.TOKEN_FILE, Config.SCOPES)
            logger.info("Loaded credentials from token file")
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            os.remove(Config.TOKEN_FILE)
    
    # If no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Refreshed access token")
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                return None
        else:
            if not os.path.exists(Config.CLIENT_SECRET_FILE):
                logger.error(f"Client secret file '{Config.CLIENT_SECRET_FILE}' not found")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.CLIENT_SECRET_FILE, 
                    Config.SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("Successfully obtained new credentials")
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                return None
        
        # Save credentials for next run
        try:
            with open(Config.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            logger.info("Saved credentials to token file")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
    
    return creds

async def get_heart_rate(service):
    """Get the latest heart rate reading"""
    try:
        now = int(time.time() * 1000000000)  # Current time in nanoseconds
        five_min_ago = now - (5 * 60 * 1000000000)  # 5 minutes ago
        
        # Get data source ID
        data_sources = service.users().dataSources().list(
            userId='me',
            dataTypeName='com.google.heart_rate.bpm'
        ).execute()
        
        if 'dataSource' not in data_sources or not data_sources['dataSource']:
            logger.warning("No heart rate data source found")
            return None, None
        
        data_source_id = data_sources['dataSource'][0]['dataStreamId']
        
        # Get the dataset
        dataset = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=data_source_id,
            datasetId=f"{five_min_ago}-{now}"
        ).execute()
        
        if 'point' in dataset and dataset['point']:
            # Get the most recent data point
            latest_point = dataset['point'][-1]
            bpm = latest_point['value'][0]['fpVal']
            timestamp_ns = int(latest_point['startTimeNanos'])
            timestamp = datetime.fromtimestamp(timestamp_ns / 1000000000)
            return bpm, timestamp
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error getting heart rate: {e}")
        return None, None

async def main():
    logger.info("="*70)
    logger.info("Starting Heart Rate Monitor with Telegram Alerts")
    logger.info(f"Alerts will trigger above {Config.HEART_RATE_THRESHOLD} BPM")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*70 + "\n")
    
    # Authenticate with Google Fit
    creds = authenticate()
    if not creds:
        logger.error("Failed to authenticate with Google Fit")
        return
    
    # Build the service
    try:
        service = build('fitness', 'v1', credentials=creds)
        logger.info("Successfully connected to Google Fit API")
    except Exception as e:
        logger.error(f"Failed to connect to Google Fit: {e}")
        return
    
    # Main monitoring loop
    last_alert_time = 0
    
    try:
        while True:
            # Get heart rate
            bpm, timestamp = await get_heart_rate(service)
            
            if bpm is not None:
                logger.info(f"Heart Rate: {bpm:.0f} BPM at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Check for high heart rate
                if bpm > Config.HEART_RATE_THRESHOLD:
                    current_time = time.time()
                    if current_time - last_alert_time > 300:  # 5 minutes cooldown
                        logger.warning(f"High heart rate detected: {bpm:.0f} BPM")
                        await send_telegram_alert(bpm, timestamp)
                        last_alert_time = current_time
            else:
                logger.warning("Could not get heart rate data")
            
            # Wait before next check
            await asyncio.sleep(Config.CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\nStopping heart rate monitor...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Heart rate monitor stopped")

if __name__ == "__main__":
    asyncio.run(main())
