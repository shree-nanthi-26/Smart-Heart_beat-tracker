import pandas as pd
import requests
from datetime import datetime

def analyze_heart_rate_by_date():
    try:
        # Read the Excel file
        df = pd.read_excel('heart_rate_data.xlsx')
        
        # Clean up column names (remove extra whitespace)
        df.columns = df.columns.str.strip()
        
        # Print available columns for debugging
        print("Available columns:", list(df.columns))
        
        # Check if we have the required columns (case insensitive)
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        bpm_col = next((col for col in df.columns if 'bpm' in col.lower()), None)
        
        if not date_col or not bpm_col:
            print("Error: Required columns not found in the data.")
            print(f"Looking for 'Date' and 'BPM' columns. Found: {list(df.columns)}")
            return None
            
        # Rename columns for consistency
        df = df.rename(columns={date_col: 'Date', bpm_col: 'BPM'})
        
        # Convert Date to datetime and extract date part
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        # Group by date and analyze
        date_analyses = []
        for date, group in df.groupby('Date'):
            date_str = date.strftime('%Y-%m-%d')
            avg_bpm = group['BPM'].mean()
            max_bpm = group['BPM'].max()
            min_bpm = group['BPM'].min()
            above_threshold = len(group[group['BPM'] > 85])
            total_readings = len(group)
            
            # Get time and BPM data if available
            time_col = next((col for col in ['Time', 'time', 'Timestamp'] if col in df.columns), None)
            
            readings = []
            if time_col:
                # If time column exists, include it in the readings
                for _, row in group.iterrows():
                    readings.append({
                        'time': str(row.get(time_col, '')),
                        'bpm': row['BPM']
                    })
            else:
                # If no time column, just include BPM values
                readings = [{'bpm': bpm} for bpm in group['BPM']]
            
            date_analyses.append({
                'date': date_str,
                'avg_bpm': round(float(avg_bpm), 1),
                'max_bpm': float(max_bpm),
                'min_bpm': float(min_bpm),
                'above_threshold': int(above_threshold),
                'total_readings': int(total_readings),
                'readings': readings
            })
        
        return date_analyses
        
    except Exception as e:
        print(f"Error analyzing data: {e}")
        return None

def send_telegram_alert(analysis):
    bot_token = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    chat_id = "6989072955"
    
    for date_data in analysis:
        # Format the message with emojis
        message = (
            f"📅 *Date: {date_data['date']}*\n"
            "📊 *Daily Heart Rate Summary*\n"
            f"• Highest: {date_data['max_bpm']} BPM\n"
            f"• Lowest: {date_data['min_bpm']} BPM\n"
            f"• Readings >85 BPM: {date_data['above_threshold']}/{date_data['total_readings']}\n\n"
            "📈 *High Readings (BPM > 85)*\n"
        )
            # Add high readings if any
        high_readings = [r for r in date_data['readings'] if r['bpm'] > 85]
        if high_readings:
            for reading in high_readings[:10]:  # Limit to first 10 high readings
                time_str = f"{reading.get('time', '')}: " if 'time' in reading else ''
                message += f"• {time_str}{reading['bpm']} BPM\n"
            if len(high_readings) > 10:
                message += f"• ... and {len(high_readings) - 10} more\n"
        else:
            message += "No readings above 85 BPM\n"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        try:
            response = requests.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {date_data['date']} analysis sent to Telegram!")
            else:
                print(f"❌ Error sending {date_data['date']} data: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error sending {date_data['date']} data: {e}")

def main():
    print("Analyzing heart rate data by date...")
    analysis = analyze_heart_rate_by_date()
    
    if analysis:
        print(f"\nFound data for {len(analysis)} date(s). Sending reports...\n")
        send_telegram_alert(analysis)
        print("\nAll reports have been sent to Telegram!")
    else:
        print("No data to analyze or error occurred.")

if __name__ == "__main__":
    main()
