import requests
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd
from pathlib import Path

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
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('fitness', 'v1', credentials=creds)

def get_heart_rate_data(service, start_time, end_time):
    """Fetch heart rate data for the specified time range"""
    data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
    dataset_id = f"{int(start_time.timestamp() * 1000000000)}-{int(end_time.timestamp() * 1000000000)}"
    
    try:
        data = service.users().dataSources().datasets() \
            .get(userId='me', dataSourceId=data_source, datasetId=dataset_id).execute()
        return data
    except Exception as e:
        print(f"Error fetching heart rate data: {e}")
        return None

def process_heart_rate_data(dataset):
    """Process heart rate data and return recent readings from the last 24 hours"""
    if 'point' not in dataset:
        return None
    
    readings = []
    
    for point in dataset['point']:
        if 'value' in point and len(point['value']) > 0:
            bpm = point['value'][0].get('fpVal')
            if bpm is not None:
                timestamp_ns = int(point['startTimeNanos'])
                timestamp = datetime.fromtimestamp(timestamp_ns / 1e9)
                status = 'HIGH' if bpm > 100 else 'NORMAL'
                readings.append({
                    'timestamp': timestamp,
                    'bpm': bpm,
                    'status': status
                })
    
    # Sort by timestamp in descending order
    readings.sort(key=lambda x: x['timestamp'], reverse=True)
    return readings

def save_to_excel(readings, filename='heart_rate_data.xlsx'):
    """Save heart rate readings to an Excel file with consistent formatting"""
    try:
        # Convert readings to DataFrame with consistent format
        data = []
        for reading in readings:
            data.append({
                'Date': reading['timestamp'].date(),
                'Time': reading['timestamp'].time(),
                'DateTime': reading['timestamp'],
                'BPM': reading['bpm'],
                'Status': reading['status']
            })
        
        df_new = pd.DataFrame(data)
        
        # Check if file exists
        filepath = Path(filename)
        if filepath.exists():
            try:
                # Read existing data, handling different column formats
                df_existing = pd.read_excel(filename)
                
                # Standardize column names and handle different formats
                column_mapping = {
                    'date': 'Date',
                    'time': 'Time',
                    'timestamp': 'DateTime',
                    'bpm': 'BPM',
                    'status': 'Status',
                    'Alert': 'Status'  # Map old 'Alert' column to 'Status'
                }
                
                # Rename columns to standard format
                df_existing = df_existing.rename(columns={k: v for k, v in column_mapping.items() 
                                                         if k in df_existing.columns})
                
                # Ensure DateTime is in datetime format
                if 'DateTime' in df_existing.columns:
                    df_existing['DateTime'] = pd.to_datetime(df_existing['DateTime'])
                
                # Combine and remove duplicates based on DateTime
                df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['DateTime'])
                
            except Exception as e:
                print(f"⚠️  Error reading existing file, creating new one: {e}")
                df_combined = df_new
        else:
            df_combined = df_new
        
        # Ensure proper data types
        if 'Date' not in df_combined.columns and 'DateTime' in df_combined.columns:
            df_combined['Date'] = pd.to_datetime(df_combined['DateTime']).dt.date
        if 'Time' not in df_combined.columns and 'DateTime' in df_combined.columns:
            df_combined['Time'] = pd.to_datetime(df_combined['DateTime']).dt.time
        if 'BPM' not in df_combined.columns and 'bpm' in df_combined.columns:
            df_combined['BPM'] = df_combined['bpm']
        if 'Status' not in df_combined.columns and 'status' in df_combined.columns:
            df_combined['Status'] = df_combined['status']
        
        # Select and order the columns we want to keep
        final_columns = ['Date', 'Time', 'DateTime', 'BPM', 'Status']
        df_combined = df_combined[[col for col in final_columns if col in df_combined.columns]]
        
        # Sort by DateTime
        if 'DateTime' in df_combined.columns:
            df_combined = df_combined.sort_values('DateTime', ascending=False)
        
        # Save to Excel with formatting
        with pd.ExcelWriter(filename, engine='openpyxl', datetime_format='yyyy-mm-dd hh:mm:ss') as writer:
            df_combined.to_excel(writer, index=False, sheet_name='HeartRateData')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['HeartRateData']
            for idx, col in enumerate(df_combined.columns):
                max_length = max(10, df_combined[col].astype(str).apply(len).max())
                worksheet.column_dimensions[chr(65+idx)].width = min(20, max_length + 2)
        
        print(f"✅ Data saved to {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to Excel: {e}")
        return False
        return False

def get_todays_readings(service):
    """Get all heart rate readings for today"""
    # Get today's date at midnight
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = datetime.now()
    
    print(f"Fetching today's data from {today} to {end_time}")
    
    dataset = get_heart_rate_data(service, today, end_time)
    if not dataset:
        print("No heart rate data available for today")
        return None
        
    readings = process_heart_rate_data(dataset)
    if not readings:
        print("No valid heart rate readings found for today")
        return None
        
    # Sort readings by timestamp (newest first)
    readings.sort(key=lambda x: x['timestamp'], reverse=True)
    return readings

def analyze_daily_readings(readings):
    """Analyze today's readings and return statistics"""
    if not readings:
        return None
        
    bpms = [r['bpm'] for r in readings]
    high_readings = [r for r in readings if r['status'] == 'HIGH']
    
    return {
        'total_readings': len(readings),
        'avg_bpm': round(sum(bpms) / len(bpms), 1) if readings else 0,
        'min_bpm': min(bpms) if readings else 0,
        'max_bpm': max(bpms) if readings else 0,
        'high_reading_count': len(high_readings),
        'high_reading_percent': round(len(high_readings) / len(readings) * 100, 1) if readings else 0,
        'latest_reading': readings[0],
        'readings_by_hour': get_readings_by_hour(readings)
    }

def get_readings_by_hour(readings):
    """Group readings by hour"""
    hourly = {}
    for reading in readings:
        hour = reading['timestamp'].replace(minute=0, second=0, microsecond=0)
        if hour not in hourly:
            hourly[hour] = []
        hourly[hour].append(reading['bpm'])
    
    # Calculate average for each hour
    hourly_avg = {}
    for hour, values in hourly.items():
        hourly_avg[hour] = round(sum(values) / len(values), 1)
    
    return hourly_avg

def format_hourly_summary(hourly_readings):
    """Format hourly readings into a readable string"""
    if not hourly_readings:
        return "  No hourly data available"
        
    lines = []
    for hour in sorted(hourly_readings.keys(), reverse=True):
        hour_str = hour.strftime("%I %p").lstrip('0')
        bpm = hourly_readings[hour]
        status = 'HIGH' if bpm > 100 else 'NORMAL'
        lines.append(f"  • {hour_str}: {bpm} BPM ({status})")
    
    return "\n".join(lines)

def send_heart_alert(hours_ago=None):
    bot_token = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    chat_id = "6989072955"
    
    try:
        service = get_authenticated_service()
        
        if hours_ago is not None:
            # Get historical data for specific hours ago
            end_time = datetime.now() - timedelta(hours=hours_ago)
            start_time = end_time - timedelta(hours=1)
            
            print(f"Fetching data from {start_time} to {end_time}")
            
            dataset = get_heart_rate_data(service, start_time, end_time)
            if not dataset:
                print("No heart rate data available for the specified time range")
                return
                
            readings = process_heart_rate_data(dataset)
            if not readings:
                print("No valid heart rate readings found for the specified time range")
                return
                
            # Sort readings by timestamp (newest first)
            readings.sort(key=lambda x: x['timestamp'], reverse=True)
            latest = readings[0]
            
            # Prepare previous readings (all available in the time range)
            previous_readings = []
            for reading in readings[1:]:
                previous_readings.append({
                    'time': reading['timestamp'].strftime("%I:%M %p"),
                    'date': reading['timestamp'].strftime("%b %d"),
                    'bpm': int(reading['bpm']),
                    'status': reading['status']
                })
            
            previous_readings_text = "\n".join(
                f"  • {r['date']} {r['time']}: {r['bpm']} BPM ({r['status']})"
                for r in previous_readings
            ) if previous_readings else "  No other readings available in this time range."
            
            # Format date and time for the latest reading
            date_str = latest['timestamp'].strftime('%A, %B %d, %Y')
            time_str = latest['timestamp'].strftime('%I:%M %p')
            
            alert_message = (
                "📊 *HISTORICAL HEART RATE SUMMARY* 📊\n"
                f"⏰ *Time Range:* {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}\n"
                f"📅 *Date:* {date_str}\n"
                f"🕒 *Latest Reading:* {time_str}\n"
                "\n"
                f"❤️ *BPM Reading:* {int(latest['bpm'])} ({latest['status']})\n"
                "\n"
                f"📉 *All Readings in This Period ({len(readings)} total):*\n"
                f"{previous_readings_text}\n\n"
                "⚠️ *Note:* This is a historical data report. "
                "Please consult with a healthcare professional for medical advice."
            )
            
        else:
            # Get today's data
            readings = get_todays_readings(service)
            if not readings:
                print("❌ No heart rate data available for today.")
                return
                
            # Save readings to Excel
            save_to_excel(readings)
            
            # Analyze today's data
            stats = analyze_daily_readings(readings)
            
            # Format the message
            latest = stats['latest_reading']
            hourly_summary = format_hourly_summary(stats['readings_by_hour'])
            
            alert_message = (
                "📊 *TODAY'S HEART RATE SUMMARY* 📊\n"
                f"📅 *Date:* {datetime.now().strftime('%A, %B %d, %Y')}\n\n"
                f"❤️ *Latest Reading:* {int(latest['bpm'])} BPM ({latest['status']}) at {latest['timestamp'].strftime('%I:%M %p')}\n"
                "\n"
                "📈 *Daily Statistics:*\n"
                f"  • Total Readings: {stats['total_readings']}\n"
                f"  • Average BPM: {stats['avg_bpm']}\n"
                f"  • Range: {stats['min_bpm']} - {stats['max_bpm']} BPM\n"
                f"  • High Readings: {stats['high_reading_count']} ({stats['high_reading_percent']}% of total)\n"
                "\n"
                "⏱ *Hourly Averages:*\n"
                f"{hourly_summary}\n\n"
                "💡 *Tip:* Regular monitoring helps track your heart health. "
                "Consult a healthcare professional if you notice any concerning patterns."
            )
        
        # Send the message
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': alert_message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        if hours_ago is not None:
            print(f"✅ Heart rate report for {hours_ago} hours ago sent successfully!")
        else:
            print("✅ Today's heart rate summary sent successfully!")
        print("Check your Telegram for the alert message.")
        
    except Exception as e:
        print(f"❌ Error sending alert: {e}")
        print("Please check your internet connection and Telegram bot settings.")

def get_recent_readings(service, minutes_ago=30):
    """Get heart rate readings from the last specified minutes"""
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=minutes_ago)
    
    print(f"Fetching data from {start_time} to {end_time}")
    
    dataset = get_heart_rate_data(service, start_time, end_time)
    if not dataset:
        print(f"No heart rate data available for the last {minutes_ago} minutes")
        return None
        
    readings = process_heart_rate_data(dataset)
    if not readings:
        print(f"No valid heart rate readings found in the last {minutes_ago} minutes")
        return None
        
    # Sort readings by timestamp (newest first)
    readings.sort(key=lambda x: x['timestamp'], reverse=True)
    return readings

def main():
    import sys
    
    try:
        service = get_authenticated_service()
        print(f"Getting the most recent heart rate readings...")
        
        # Get readings from the last 30 minutes
        readings = get_recent_readings(service, minutes_ago=30)
        
        if not readings:
            print("❌ No recent heart rate data available.")
            return
            
        latest = readings[0]
        
        # Prepare previous readings (up to 5 most recent)
        previous_readings = []
        for reading in readings[1:6]:  # Get up to 5 previous readings
            previous_readings.append({
                'time': reading['timestamp'].strftime("%I:%M %p"),
                'bpm': int(reading['bpm']),
                'status': reading['status']
            })
        
        previous_readings_text = "\n".join(
            f"  • {r['time']}: {r['bpm']} BPM ({r['status']})"
            for r in previous_readings
        ) if previous_readings else "  No other recent readings available."
        
        # Format the alert message
        alert_message = (
            "❤️ *LATEST HEART RATE UPDATE* ❤️\n"
            f"🕒 *Time:* {latest['timestamp'].strftime('%I:%M %p')}\n"
            f"📅 *Date:* {latest['timestamp'].strftime('%A, %B %d, %Y')}\n"
            "\n"
            f"💓 *Current BPM:* {int(latest['bpm'])} ({latest['status']})\n"
            "\n"
            "⏱ *Recent Readings:*\n"
            f"{previous_readings_text}\n\n"
        )
        
        # Add alert if heart rate is high
        if latest['bpm'] > 100:
            alert_message += "⚠️ *ALERT: High heart rate detected!*\n"
            alert_message += "Please take a moment to rest and monitor your condition.\n"
            
        alert_message += "\n💡 *Note:* This is an automated alert. "
        alert_message += "Contact a healthcare professional if you have concerns about your heart rate."
        
        # Send the message
        bot_token = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
        chat_id = "6989072955"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': alert_message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        print("✅ Latest heart rate update sent successfully!")
        print(f"📊 Sent {len(readings)} reading(s) from the last 30 minutes.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your internet connection and API settings.")

if __name__ == "__main__":
    main()
