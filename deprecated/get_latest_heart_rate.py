import os
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_authenticated_service():
    """Get authenticated Google Fit service"""
    SCOPES = ['https://www.googleapis.com/auth/fitness.heart_rate.read']
    creds = None
    
    # Load existing token if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('fitness', 'v1', credentials=creds)

def get_heart_rate_data(service, start_time, end_time):
    """Fetch heart rate data for the specified time range"""
    # Format times in nanoseconds
    start_ns = int(start_time.timestamp() * 1e9)
    end_ns = int(end_time.timestamp() * 1e9)
    
    # Format times in milliseconds for the API
    start_ms = int(start_time.timestamp() * 1000)
    end_ms = int(end_time.timestamp() * 1000)
    
    try:
        # Get the data source ID for heart rate
        data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
        
        # Get the dataset
        dataset = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=data_source,
            datasetId=f"{start_ms}000000-{end_ms}000000"
        ).execute()
        
        # Process the data points
        data_points = []
        for point in dataset.get('point', []):
            for value in point.get('value', []):
                if 'fpVal' in value:
                    timestamp_ns = int(point['startTimeNanos'])
                    timestamp = datetime.fromtimestamp(timestamp_ns / 1e9)
                    bpm = value['fpVal']
                    
                    data_points.append({
                        'timestamp': timestamp,
                        'bpm': bpm,
                        'status': 'HIGH' if bpm > 99 else 'NORMAL'
                    })
        
        return data_points
        
    except Exception as e:
        print(f"Error fetching heart rate data: {e}")
        return []

def main():
    print("Fetching latest heart rate data...")
    
    try:
        # Set up time range (last 24 hours)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Get authenticated service
        service = get_authenticated_service()
        print("✅ Connected to Google Fit API")
        
        # Get heart rate data
        print(f"Fetching data from {start_time} to {end_time}...")
        heart_data = get_heart_rate_data(service, start_time, end_time)
        
        if not heart_data:
            print("\nNo heart rate data found for the specified time range.")
            print("Please ensure you have heart rate data in your Google Fit account.")
            input("\nPress Enter to exit...")
            return
        
        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(heart_data)
        output_file = 'latest_heart_rate.csv'
        df.to_csv(output_file, index=False)
        
        # Print summary
        print("\n" + "="*60)
        print(f"✅ Success! Saved {len(df)} heart rate readings to {output_file}")
        print("\nLatest 5 readings:")
        print(df.tail().to_string(index=False))
        
        # Check for high heart rate
        high_readings = df[df['status'] == 'HIGH']
        if not high_readings.empty:
            print(f"\n⚠️  WARNING: Found {len(high_readings)} high heart rate readings (>99 BPM)")
            print(high_readings[['timestamp', 'bpm']].to_string(index=False))
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
