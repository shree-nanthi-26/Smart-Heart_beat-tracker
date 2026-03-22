import os
import time
import pandas as pd
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def authenticate():
    """Simple authentication with Google Fit"""
    try:
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json')
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', 
                    ['https://www.googleapis.com/auth/fitness.heart_rate.read']
                )
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return creds
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def get_heart_rate_data():
    """Fetch heart rate data from Google Fit"""
    try:
        creds = authenticate()
        if not creds:
            print("Failed to authenticate")
            return []

        service = build('fitness', 'v1', credentials=creds)
        
        # Get current time in nanoseconds
        now = int(time.time() * 1000000000)
        one_day_ago = now - (24 * 60 * 60 * 1000000000)  # 24 hours ago
        
        # Format times in milliseconds for the API
        start = one_day_ago // 1000000
        end = now // 1000000
        
        # Fetch heart rate data
        data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
        dataset = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=data_source,
            datasetId=f"{start}000000-{end}000000"
        ).execute()
        
        heart_rates = []
        for point in dataset.get('point', []):
            for value in point.get('value', []):
                if 'fpVal' in value:
                    timestamp = int(point['startTimeNanos']) // 1000000000
                    dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    heart_rates.append({
                        'DateTime': dt,
                        'BPM': value['fpVal'],
                        'Alert': 'HIGH' if value['fpVal'] > 99 else 'NORMAL'
                    })
        
        return heart_rates
        
    except Exception as e:
        print(f"Error fetching heart rate data: {e}")
        return []

def main():
    print("Starting Heart Rate Monitor...")
    print("Fetching heart rate data (this may take a moment)...")
    
    # Get heart rate data
    heart_data = get_heart_rate_data()
    
    if not heart_data:
        print("\nNo heart rate data found or error occurred.")
        print("Please ensure you have heart rate data in your Google Fit account.")
        input("\nPress Enter to exit...")
        return
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(heart_data)
    output_file = 'heart_rate_data.csv'
    df.to_csv(output_file, index=False)
    
    # Display summary
    print("\n" + "="*50)
    print(f"Success! Heart rate data saved to {output_file}")
    print(f"Total readings: {len(df)}")
    
    high_readings = df[df['Alert'] == 'HIGH']
    if not high_readings.empty:
        print(f"\n⚠️  High heart rate detected! ({len(high_readings)} readings > 99 BPM)")
        print(high_readings[['DateTime', 'BPM']].to_string(index=False))
    else:
        print("\n✅ No high heart rate readings detected.")
    
    print("\n" + "="*50)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
