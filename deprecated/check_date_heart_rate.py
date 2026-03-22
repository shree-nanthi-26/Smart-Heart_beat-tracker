import pandas as pd
from datetime import datetime

def get_heart_rate_by_date(target_date_str):
    """Get heart rate data for a specific date from all available CSV files."""
    try:
        # Try to parse the target date
        try:
            target_date = datetime.strptime(target_date_str, '%d-%m-%y').date()
        except ValueError:
            return {"error": "Invalid date format. Please use DD-MM-YY format."}
        
        data_found = False
        results = {
            'date': target_date_str,
            'readings': [],
            'summary': {}
        }
        
        # Check latest_heart_rate.csv
        if os.path.exists('latest_heart_rate.csv'):
            df = pd.read_csv('latest_heart_rate.csv')
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                daily_data = df[df['date'] == target_date]
                if not daily_data.empty:
                    data_found = True
                    for _, row in daily_data.iterrows():
                        results['readings'].append({
                            'time': row['timestamp'].strftime('%H:%M:%S'),
                            'bpm': int(row['bpm']),
                            'status': row['status']
                        })
        
        # Check heart_rate_data.csv
        if os.path.exists('heart_rate_data.csv'):
            df = pd.read_csv('heart_rate_data.csv')
            if not df.empty:
                df['DateTime'] = pd.to_datetime(df['DateTime'])
                df['date'] = df['DateTime'].dt.date
                daily_data = df[df['date'] == target_date]
                if not daily_data.empty:
                    data_found = True
                    for _, row in daily_data.iterrows():
                        results['readings'].append({
                            'time': row['DateTime'].strftime('%H:%M:%S'),
                            'bpm': int(row['BPM']),
                            'status': row['Alert']
                        })
        
        # Generate summary if data was found
        if data_found and results['readings']:
            bpm_values = [r['bpm'] for r in results['readings']]
            results['summary'] = {
                'total_readings': len(results['readings']),
                'avg_bpm': round(sum(bpm_values) / len(bpm_values), 1),
                'min_bpm': min(bpm_values),
                'max_bpm': max(bpm_values),
                'high_readings': sum(1 for r in results['readings'] if r['bpm'] > 90)
            }
            
            # Sort readings by time
            results['readings'].sort(key=lambda x: x['time'])
            
        return results if data_found else {"error": f"No data found for {target_date_str}"}
        
    except Exception as e:
        return {"error": f"Error processing data: {str(e)}"}

def format_results(results):
    """Format the results into a human-readable string."""
    if 'error' in results:
        return f"❌ {results['error']}"
    
    output = [
        f"📅 *Heart Rate Data for {results['date']}*\n",
        f"📊 *Summary:*",
        f"• Total Readings: {results['summary']['total_readings']}",
        f"• Average BPM: {results['summary']['avg_bpm']}",
        f"• Min BPM: {results['summary']['min_bpm']}",
        f"• Max BPM: {results['summary']['max_bpm']}",
        f"• High Readings (>90 BPM): {results['summary']['high_readings']}\n"
    ]
    
    if results['readings']:
        output.append("📈 *Readings (Time - BPM - Status):*")
        for reading in results['readings']:
            status_emoji = "⚠️" if reading['bpm'] > 90 else "✅"
            output.append(f"• {reading['time']} - {reading['bpm']} BPM - {reading['status']} {status_emoji}")
    
    return "\n".join(output)

def send_to_telegram(message):
    """Send the formatted message to Telegram."""
    BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
    CHAT_ID = "6989072955"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

if __name__ == "__main__":
    import os
    import sys
    import requests
    
    # Default to today's date if no date provided
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%d-%m-%y')
    
    print(f"Fetching heart rate data for {target_date}...")
    results = get_heart_rate_by_date(target_date)
    formatted_message = format_results(results)
    
    # Print to console
    print("\n" + "="*50)
    print(formatted_message)
    print("="*50 + "\n")
    
    # Ask if user wants to send to Telegram
    if 'error' not in results:
        send_choice = input("Would you like to send this to Telegram? (y/n): ").strip().lower()
        if send_choice == 'y':
            if send_to_telegram(formatted_message):
                print("✅ Data sent to Telegram successfully!")
            else:
                print("❌ Failed to send to Telegram.")
    
    input("\nPress Enter to exit...")
