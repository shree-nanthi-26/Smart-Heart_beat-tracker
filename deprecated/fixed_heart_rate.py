import os
import time
import pandas as pd
import asyncio
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Configuration
SCOPES = ["https://www.googleapis.com/auth/fitness.heart_rate.read"]
OUTPUT_FILE = "heart_rate_data.csv"

# Telegram configuration (optional)
TELEGRAM_BOT_TOKEN = "8168004449:AAHsY9KsZN2ZGU3EeEVlV5sAXwdGXpal_ss"
TELEGRAM_CHAT_ID = "7332916002"
TELEGRAM_ENABLED = False

def authenticate():
    """Authenticate with Google Fit API"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

async def main():
    print("Starting heart rate monitoring...")
    
    try:
        # Authenticate
        creds = authenticate()
        if not creds or not creds.valid:
            print("Failed to authenticate with Google Fit")
            return
            
        print("Successfully authenticated with Google Fit")
        
        # Build service
        service = build("fitness", "v1", credentials=creds)
        print("Connected to Google Fit API\n")
        
        # Get heart rate data
        end_time = int(time.time() * 1000000000)  # nanoseconds
        start_time = end_time - (24 * 60 * 60 * 1000000000)  # 1 day ago
        
        print(f"Fetching heart rate data from {datetime.fromtimestamp(start_time/1e9)} to {datetime.fromtimestamp(end_time/1e9)}")
        
        data = service.users().dataset().aggregate(
            userId="me",
            body={
                "aggregateBy": [{"dataTypeName": "com.google.heart_rate.bpm"}],
                "bucketByTime": {"durationMillis": 60000},  # 1-minute intervals
                "startTimeMillis": start_time // 1000000,
                "endTimeMillis": end_time // 1000000,
            }
        ).execute()
        
        # Process data
        heart_data = []
        high_heart_rate_alerts = []
        
        for bucket in data.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point["value"]:
                        start_time_seconds = int(point["startTimeNanos"]) / 1e9
                        bpm = val.get("fpVal")
                        if bpm is None:
                            continue
                            
                        datetime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_seconds))
                        is_high = bpm > 85  # Alert if heart rate is above 85 BPM
                        
                        if is_high:
                            high_heart_rate_alerts.append({"time": datetime_str, "bpm": bpm})
                        
                        heart_data.append({
                            "DateTime": datetime_str,
                            "BPM": bpm,
                            "Alert": "HIGH" if is_high else "NORMAL"
                        })
        
        # Save to CSV
        if heart_data:
            try:
                df = pd.DataFrame(heart_data)
                df.to_csv(OUTPUT_FILE, index=False)
                
                print(f"\nSuccess! Heart rate data saved to {OUTPUT_FILE}")
                print(f"Total readings: {len(df)}")
                
                if high_heart_rate_alerts:
                    print(f"\nWARNING: {len(high_heart_rate_alerts)} high heart rate readings detected!")
                    print("-" * 60)
                    for alert in high_heart_rate_alerts[-5:]:  # Show last 5 alerts
                        print(f"{alert['time']}: {alert['bpm']} BPM")
                    if len(high_heart_rate_alerts) > 5:
                        print(f"... and {len(high_heart_rate_alerts) - 5} more")
                    print("-" * 60)
            except Exception as e:
                print(f"Error saving data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def run_async():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'loop' in locals():
            loop.close()
        input("Press Enter to exit...")

if __name__ == "__main__":
    run_async()
