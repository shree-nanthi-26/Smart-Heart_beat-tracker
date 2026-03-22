from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

def check_data_sources():
    """Check available data sources in Google Fit"""
    try:
        # Try to get existing credentials
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
        
        # Build the fitness service
        service = build('fitness', 'v1', credentials=creds)
        
        # List all data sources
        print("\nAvailable data sources:")
        print("=" * 50)
        sources = service.users().dataSources().list(userId='me').execute()
        
        if 'dataSource' in sources:
            for i, source in enumerate(sources['dataSource'], 1):
                print(f"\n{i}. {source.get('name', 'Unnamed')}")
                print(f"   Type: {source.get('dataType', {}).get('name')}")
                print(f"   Device: {source.get('device', {}).get('model', 'Unknown')}")
        else:
            print("No data sources found!")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    print("Checking Google Fit data sources...")
    check_data_sources()
