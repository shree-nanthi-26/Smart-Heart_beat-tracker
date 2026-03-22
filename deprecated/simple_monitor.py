import os
import time
import pandas as pd
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Configuration
SCOPES = ["https://www.googleapis.com/auth/fitness.heart_rate.read"]
OUTPUT_FILE = "heart_rate_data.csv"

def authenticate():
    """Authenticate with Google Fit API"""
    creds = None
    
    # Check for existing token
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            print("✓ Loaded existing credentials")
        except Exception as e:
            print(f"! Error loading credentials: {e}")
            os.remove("token.json")  # Remove invalid token
    
    # If no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✓ Refreshed access token")
            except Exception as e:
                print(f"! Error refreshing token: {e}")
                return None
        else:
            if not os.path.exists("client_secret.json"):
                print("! Error: client_secret.json not found")
                return None
                
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json", 
                    SCOPES
                )
                creds = flow.run_console()
                print("✓ Successfully authenticated")
            except Exception as e:
                print(f"! Authentication error: {e}")
                return None
        
        # Save credentials for next run
        try:
            with open("token.json", "w") as token:
                token.write(creds.to_json())
            print("✓ Saved credentials")
        except Exception as e:
            print(f"! Error saving credentials: {e}")
    
    return creds

def get_heart_rate_data(service):
    """Fetch heart rate data from Google Fit"""
    try:
        end_time = int(time.time() * 1000000000)  # Current time in nanoseconds
        start_time = end_time - (24 * 60 * 60 * 1000000000)  # Last 24 hours
        
        print("\nFetching heart rate data...")
        
        data = service.users().dataset().aggregate(
            userId="me",
            body={
                "aggregateBy": [{"dataTypeName": "com.google.heart_rate.bpm"}],
                "bucketByTime": {"durationMillis": 60000},  # 1-minute intervals
                "startTimeMillis": start_time // 1000000,
                "endTimeMillis": end_time // 1000000,
            }
        ).execute()
        
        # Process the data
        heart_rates = []
        for bucket in data.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point.get("value", []):
                        bpm = val.get("fpVal")
                        if bpm is not None:
                            timestamp = int(point["startTimeNanos"]) // 1000000000
                            dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            heart_rates.append({
                                "timestamp": dt,
                                "bpm": bpm,
                                "status": "HIGH" if bpm > 90 else "NORMAL"
                            })
        
        return heart_rates
        
    except Exception as e:
        print(f"! Error fetching heart rate data: {e}")
        return []

def main():
    print("\n" + "="*60)
    print("SIMPLE HEART RATE MONITOR")
    print("="*60)
    
    # Authenticate
    creds = authenticate()
    if not creds:
        print("\n❌ Failed to authenticate. Please check your credentials.")
        return
    
    # Build the service
    try:
        service = build("fitness", "v1", credentials=creds)
        print("\n✓ Connected to Google Fit API")
    except Exception as e:
        print(f"\n❌ Error connecting to Google Fit: {e}")
        return
    
    # Main monitoring loop
    try:
        while True:
            # Get heart rate data
            heart_rates = get_heart_rate_data(service)
            
            if heart_rates:
                # Get the latest reading
                latest = heart_rates[-1]
                status = "🟢" if latest["status"] == "NORMAL" else "🔴"
                print(f"\n{status} Latest reading: {latest['bpm']} BPM at {latest['timestamp']}")
                
                # Save to CSV
                df = pd.DataFrame(heart_rates)
                df.to_csv(OUTPUT_FILE, index=False)
                print(f"✓ Data saved to {OUTPUT_FILE}")
            else:
                print("\n⚠️  No heart rate data available")
            
            # Wait before next check (5 minutes)
            print("\nNext check in 5 minutes...")
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
    
    print("\n✓ Monitoring stopped")

if __name__ == "__main__":
    main()
