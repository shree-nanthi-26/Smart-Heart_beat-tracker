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
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('fitness', 'v1', credentials=creds)

def get_all_heart_rate_data(service):
    """Fetch all available heart rate data"""
    try:
        data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
        
        # Get the earliest available data point
        data_sources = service.users().dataSources().list(userId='me').execute()
        earliest_data = None
        
        for source in data_sources.get('dataSource', []):
            if source.get('dataType', {}).get('name') == 'com.google.heart_rate.bpm':
                earliest_data = int(source.get('dataQualityStandard', [{}])[0].get('minStartTimeNs', '0'))
                break
        
        if not earliest_data:
            print("No heart rate data source found")
            return []
        
        # Set time range from earliest data to now
        end_time = int(time.time() * 1000000000)  # Current time in nanoseconds
        start_time = max(earliest_data, end_time - (365 * 24 * 60 * 60 * 1000000000))  # Max 1 year back
        
        print(f"Fetching all heart rate data from {datetime.fromtimestamp(start_time/1e9)} to {datetime.fromtimestamp(end_time/1e9)}")
        
        # Get data in chunks to avoid timeouts
        chunk_size = 30 * 24 * 60 * 60 * 1000000000  # 30 days in nanoseconds
        all_data = []
        
        current_start = start_time
        while current_start < end_time:
            current_end = min(current_start + chunk_size, end_time)
            print(f"Fetching data from {datetime.fromtimestamp(current_start/1e9)} to {datetime.fromtimestamp(current_end/1e9)}")
            
            dataset = service.users().dataSources().datasets().get(
                userId='me',
                dataSourceId=data_source,
                datasetId=f"{current_start//1000000}-{current_end//1000000}"
            ).execute()
            
            for point in dataset.get('point', []):
                for value in point.get('value', []):
                    if 'fpVal' in value:
                        timestamp_ns = int(point['startTimeNanos'])
                        timestamp = datetime.fromtimestamp(timestamp_ns / 1e9)
                        bpm = value['fpVal']
                        
                        all_data.append({
                            'Date': timestamp.strftime('%Y-%m-%d'),
                            'Time': timestamp.strftime('%H:%M:%S'),
                            'DateTime': timestamp,
                            'BPM': bpm,
                            'Status': 'HIGH' if bpm > 99 else 'NORMAL'
                        })
            
            current_start = current_end + 1
            
        return all_data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def main():
    print("Fetching ALL historical heart rate data...")
    
    try:
        # Get authenticated service
        service = get_authenticated_service()
        print("✅ Connected to Google Fit API")
        
        # Get all heart rate data
        heart_data = get_all_heart_rate_data(service)
        
        if not heart_data:
            print("\nNo heart rate data found.")
            print("Please ensure you have heart rate data in your Google Fit account.")
            input("\nPress Enter to exit...")
            return
        
        # Convert to DataFrame and sort by date
        df = pd.DataFrame(heart_data).sort_values('DateTime')
        
        # Save to CSV
        output_file = 'all_heart_rate_data.csv'
        df.to_csv(output_file, index=False)
        
        # Print summary
        print("\n" + "="*60)
        print(f"✅ Success! Saved {len(df)} heart rate readings to {output_file}")
        print(f"Date range: {df['DateTime'].min()} to {df['DateTime'].max()}")
        
        # Show high heart rate summary
        high_readings = df[df['Status'] == 'HIGH']
        if not high_readings.empty:
            print(f"\n⚠️  Found {len(high_readings)} high heart rate readings (>99 BPM):")
            print(high_readings[['Date', 'Time', 'BPM']].to_string(index=False))
        else:
            print("\n✅ No high heart rate readings found.")
        
        print("\nFirst 5 readings:")
        print(df[['Date', 'Time', 'BPM', 'Status']].head().to_string(index=False))
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
