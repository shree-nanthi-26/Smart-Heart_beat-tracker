import os
import time
import pandas as pd
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Google Fit API configuration
SCOPES = ['https://www.googleapis.com/auth/fitness.heart_rate.read']
CLIENT_SECRETS_FILE = 'client_secret.json'  # You'll need to download this from Google Cloud Console
TOKEN_FILE = 'token.json'

# Alert threshold (beats per minute)
HEART_RATE_THRESHOLD = 100

def get_credentials():
    """Get valid user credentials from storage or prompt user to log in."""
    creds = None
    
    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            os.remove(TOKEN_FILE)
            return get_credentials()
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                os.remove(TOKEN_FILE)
                return get_credentials()
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                
            except Exception as e:
                logger.error(f"Error getting credentials: {e}")
                return None
    
    return creds

def get_heart_rate_data(service):
    """Get heart rate data from Google Fit."""
    now = int(time.time() * 1000000000)  # Current time in nanoseconds
    one_hour_ago = now - (60 * 60 * 1000000000)  # 1 hour ago in nanoseconds
    
    try:
        # Get data source ID for heart rate
        data_sources = service.users().dataSources().list(
            userId='me',
            dataTypeName='com.google.heart_rate.bpm'
        ).execute()
        
        if 'dataSource' not in data_sources or not data_sources['dataSource']:
            logger.warning("No heart rate data source found")
            return None
            
        data_source_id = data_sources['dataSource'][0]['dataStreamId']
        
        # Get dataset
        dataset = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=data_source_id,
            datasetId=f"{one_hour_ago}-{now}"
        ).execute()
        
        return dataset
        
    except Exception as e:
        logger.error(f"Error getting heart rate data: {e}")
        return None

def process_heart_rate_data(dataset):
    """Process heart rate data and return the latest reading."""
    if not dataset or 'point' not in dataset or not dataset['point']:
        return None
    
    # Get the most recent data point
    latest_point = dataset['point'][-1]
    
    # Extract heart rate and timestamp
    heart_rate = latest_point['value'][0]['fpVal']
    timestamp_ns = int(latest_point['startTimeNanos'])
    timestamp = datetime.fromtimestamp(timestamp_ns / 1e9)
    
    return {
        'heart_rate': heart_rate,
        'timestamp': timestamp,
        'timestamp_ns': timestamp_ns
    }

def main():
    """Main function to run the heart rate monitor."""
    # Check if client_secret.json exists
    if not os.path.exists('client_secret.json'):
        logger.error("""
        Error: client_secret.json not found.
        
        To run this application, you need to:
        1. Go to Google Cloud Console: https://console.cloud.google.com/
        2. Create a new project or select an existing one
        3. Enable the Fitness API for your project
        4. Configure the OAuth consent screen
        5. Create OAuth 2.0 credentials (OAuth client ID)
        6. Download the credentials as client_secret.json
        7. Place the file in this directory: %s
        """ % os.getcwd())
        return
    
    # Get credentials
    creds = get_credentials()
    if not creds:
        logger.error("Failed to obtain credentials. Exiting.")
        return
    
    # Build the service
    try:
        service = build('fitness', 'v1', credentials=creds)
    except Exception as e:
        logger.error(f"Error building service: {e}")
        return
    
    logger.info("Heart Rate Monitor Started!")
    logger.info(f"Alerts will be triggered for heart rate > {HEART_RATE_THRESHOLD} BPM")
    
    try:
        while True:
            # Get heart rate data
            dataset = get_heart_rate_data(service)
            
            if dataset:
                data = process_heart_rate_data(dataset)
                
                if data:
                    hr = data['heart_rate']
                    timestamp = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Log the heart rate
                    logger.info(f"Heart Rate: {hr:.0f} BPM at {timestamp}")
                    
                    # Check for high heart rate
                    if hr > HEART_RATE_THRESHOLD:
                        logger.warning(f"⚠️  HIGH HEART RATE ALERT: {hr:.0f} BPM at {timestamp}")
            
            # Wait before next reading
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        logger.info("\nHeart Rate Monitor Stopped.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
