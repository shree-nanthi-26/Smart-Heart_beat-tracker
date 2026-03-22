import os
import time
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope for heart rate data
SCOPES = ["https://www.googleapis.com/auth/fitness.heart_rate.read"]

# Authenticate and create token.json
def authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def fetch_heart_rate():
    creds = authenticate()
    service = build("fitness", "v1", credentials=creds)

    # Time range (last 7 days)
    end_time = int(time.time() * 1000)
    start_time = end_time - 7 * 86400000

    body = {
        "aggregateBy": [{"dataTypeName": "com.google.heart_rate.bpm"}],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_time,
        "endTimeMillis": end_time
    }

    dataset = service.users().dataset().aggregate(userId="me", body=body).execute()

    rows = []
    for bucket in dataset.get("bucket", []):
        for dataset in bucket["dataset"]:
            for point in dataset.get("point", []):
                for val in point["value"]:
                    rows.append({
                        "Date": time.strftime('%Y-%m-%d', time.localtime(int(point["startTimeNanos"]) / 1e9)),
                        "HeartRate_BPM": val["fpVal"]
                    })

    df = pd.DataFrame(rows)
    df.to_excel("heart_rate_data.xlsx", index=False)
    print("✅ Heart rate data saved to heart_rate_data.xlsx")

if __name__ == "__main__":
    fetch_heart_rate()
