from send_alert_now import get_authenticated_service, get_heart_rate_data, process_heart_rate_data
from datetime import datetime, timedelta

def get_recent_heart_rate():
    try:
        # Authenticate and get the service
        service = get_authenticated_service()
        
        # Get data from the last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Fetch heart rate data
        dataset = get_heart_rate_data(service, start_time, end_time)
        if not dataset:
            print("No heart rate data available")
            return
            
        # Process the data
        readings = process_heart_rate_data(dataset)
        if not readings:
            print("No valid heart rate readings found")
            return
        
        # Display the 10 most recent readings
        print("\n=== MOST RECENT HEART RATE READINGS ===")
        print(f"Showing up to 10 most recent readings from the last 24 hours\n")
        
        for i, reading in enumerate(readings[:10], 1):
            time_str = reading['timestamp'].strftime('%Y-%m-%d %H:%M')
            status_emoji = '🔴' if reading['status'] == 'HIGH' else '🟢'
            print(f"{i}. {time_str} - {int(reading['bpm'])} BPM {status_emoji} ({reading['status']})")
        
        # Show summary
        total_readings = len(readings)
        high_readings = sum(1 for r in readings if r['status'] == 'HIGH')
        avg_bpm = sum(r['bpm'] for r in readings) / len(readings)
        
        print(f"\n=== SUMMARY ===")
        print(f"Total readings (24h): {total_readings}")
        print(f"High readings: {high_readings} ({(high_readings/total_readings)*100:.1f}%)")
        print(f"Average BPM: {avg_bpm:.1f}")
        
        # Send notification
        print("\nSending notification...")
        from send_alert_now import send_heart_alert
        send_heart_alert()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_recent_heart_rate()
