import os
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def authenticate():
    """Authenticate with Google Fit API"""
    print("Starting authentication...")
    creds = None
    if os.path.exists('token.json'):
        print("Found token.json file")
        creds = Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        print("No valid credentials found")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("No valid refresh token, starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', 
                ["https://www.googleapis.com/auth/fitness.heart_rate.read"]
            )
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("Token saved to token.json")
    
    return creds

def main():
    print("Testing Google Fit connection...")
    try:
        creds = authenticate()
        if not creds or not creds.valid:
            print("❌ Failed to authenticate with Google Fit")
            return
            
        print("✅ Successfully authenticated with Google Fit")
        
        # Build service
        print("Building service...")
        service = build("fitness", "v1", credentials=creds)
        print("✅ Connected to Google Fit API")
        
        # Simple test query
        print("\nTesting data source access...")
        data_sources = service.users().dataSources().list(userId='me').execute()
        print(f"Found {len(data_sources.get('dataSource', []))} data sources")
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
