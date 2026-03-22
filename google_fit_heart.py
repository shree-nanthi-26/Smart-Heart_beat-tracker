import os
import asyncio
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Google API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Third-party imports
import pandas as pd
from twilio.rest import Client

# Local imports
try:
    from telegram_bot import TelegramBot
except ImportError:
    TelegramBot = None

# Load environment variables
load_dotenv()

# Configuration
class Config:
    # Google Fit API
    SCOPES = ["https://www.googleapis.com/auth/fitness.heart_rate.read"]
    CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE", "google-services.json")
    TOKEN_FILE = "token.json"
    
    # Heart rate monitoring
    HEART_RATE_THRESHOLD = int(os.getenv("HEART_RATE_THRESHOLD", 100))  # BPM
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))  # seconds
    
    # Alert settings
    ALERT_COOLDOWN = 300  # 5 minutes between alerts (in seconds)
    
    # Twilio configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    ALERT_PHONE_NUMBER = os.getenv("ALERT_PHONE_NUMBER")
    
    # Telegram configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Logging
    LOG_FILE = "heart_rate_monitor.log"
    LOG_LEVEL = logging.INFO

# Set up logging
def setup_logging():
    """Configure logging for the application."""
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

# Initialize Telegram bot if configured
telegram_bot = None
if TelegramBot and Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID:
    if (Config.TELEGRAM_BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN" and
            Config.TELEGRAM_CHAT_ID != "YOUR_CHAT_ID"):
        try:
            telegram_bot = TelegramBot(token=Config.TELEGRAM_BOT_TOKEN, 
                                    chat_id=Config.TELEGRAM_CHAT_ID)
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            telegram_bot = None

async def send_telegram_alert(heart_rate: float, timestamp: datetime) -> bool:
    """Send an alert message to Telegram."""
    if not telegram_bot:
        return False
    
    try:
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        await telegram_bot.send_alert(heart_rate=heart_rate, timestamp=timestamp_str)
        logger.info(f"Telegram alert sent for heart rate: {heart_rate} BPM")
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False

def send_sms_alert(heart_rate: float, timestamp: datetime) -> bool:
    """Send an SMS alert using Twilio."""
    if not all([Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN, 
               Config.TWILIO_PHONE_NUMBER, Config.ALERT_PHONE_NUMBER]):
        return False
    
    try:
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        message = client.messages.create(
            body=(
                f"🚨 HIGH HEART RATE ALERT!\n\n"
                f"Heart Rate: {heart_rate:.0f} BPM\n"
                f"Time: {timestamp_str}\n\n"
                "Please check your health immediately!"
            ),
            from_=Config.TWILIO_PHONE_NUMBER,
            to=Config.ALERT_PHONE_NUMBER
        )
        
        logger.info(f"SMS alert sent to {Config.ALERT_PHONE_NUMBER} (SID: {message.sid})")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS alert: {e}")
        return False

def authenticate():
    """Authenticate with Google Fit API."""
    creds = None
    if os.path.exists(Config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(Config.TOKEN_FILE, Config.SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(Config.CLIENT_SECRET_FILE):
                logger.error(f"Client secret file not found: {Config.CLIENT_SECRET_FILE}")
                return None
                
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.CLIENT_SECRET_FILE, Config.SCOPES)
                creds = flow.run_local_server(port=0)
                with open(Config.TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                return None
    
    return creds

async def main():
    logger.info("Starting heart rate monitoring...")
    
    creds = authenticate()
    if not creds:
        logger.error("Failed to authenticate. Exiting.")
        return

    try:
        service = build('fitness', 'v1', credentials=creds)
        logger.info("Successfully connected to Google Fit API")
        
        heart_data = []
        high_heart_rate_alerts = []
        
        while True:
            try:
                # Get heart rate data
                now_ns = int(time.time() * 1000000000)
                one_hour_ago_ns = now_ns - (60 * 60 * 1000000000)
                
                # Get data sources
                data_sources = service.users().dataSources().list(
                    userId='me',
                    dataTypeName='com.google.heart_rate.bpm'
                ).execute()
                
                if 'dataSource' not in data_sources or not data_sources['dataSource']:
                    logger.warning("No heart rate data source found.")
                    await asyncio.sleep(Config.CHECK_INTERVAL)
                    continue
                
                data_source_id = data_sources['dataSource'][0]['dataStreamId']
                
                # Get the dataset
                dataset = service.users().dataSources().datasets().get(
                    userId='me',
                    dataSourceId=data_source_id,
                    datasetId=f"{one_hour_ago_ns}-{now_ns}"
                ).execute()
                
                if 'point' in dataset and dataset['point']:
                    latest_point = dataset['point'][-1]
                    bpm = latest_point['value'][0]['fpVal']
                    timestamp_ns = int(latest_point['startTimeNanos'])
                    timestamp = datetime.fromtimestamp(timestamp_ns / 1000000000)
                    datetime_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    
                    logger.info(f"Heart Rate: {bpm:.0f} BPM at {datetime_str}")
                    
                    data_entry = {
                        'DateTime': datetime_str,
                        'BPM': bpm,
                        'Alert': 'NORMAL'
                    }
                    
                    # Check for high heart rate
                    if bpm > Config.HEART_RATE_THRESHOLD:
                        data_entry['Alert'] = 'HIGH'
                        logger.warning(f"HIGH HEART RATE DETECTED: {bpm:.0f} BPM")
                        
                        # Save to alerts list
                        high_heart_rate_alerts.append({'bpm': bpm, 'time': datetime_str})
                        
                        # Log to file
                        with open('heart_rate_log.txt', 'a') as f:
                            f.write(f"{datetime_str} - {bpm:.0f} BPM\n")
                        
                        # Send alerts
                        send_sms_alert(bpm, timestamp)
                        await send_telegram_alert(bpm, timestamp)
                    
                    heart_data.append(data_entry)
                
                await asyncio.sleep(Config.CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
                
    except KeyboardInterrupt:
        logger.info("Stopping heart rate monitor...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # Save to Excel before exiting
        if heart_data:
            try:
                df = pd.DataFrame(heart_data)
                df.to_excel("heart_rate_data.xlsx", index=False)
                logger.info("Heart rate data saved to heart_rate_data.xlsx")
                
                if high_heart_rate_alerts:
                    print("\n" + "🚨"*10 + " ALERT SUMMARY " + "🚨"*10)
                    for alert in high_heart_rate_alerts:
                        print(f"   • {alert['bpm']:.0f} BPM at {alert['time']}")
                    print("="*35 + "\n")
            except Exception as e:
                logger.error(f"Error saving data to Excel: {e}")
        
        logger.info("Heart rate monitor stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
