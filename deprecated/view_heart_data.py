import pandas as pd
from datetime import datetime

def view_heart_rate_data():
    try:
        # Read the Excel file
        df = pd.read_excel('heart_rate_data.xlsx')
        
        # Clean up the data
        if 'timestamp' in df.columns:
            # New format
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp', 'bpm', 'status']].sort_values('timestamp', ascending=False)
        else:
            # Old format
            df = df[['DateTime', 'BPM', 'Alert']].copy()
            df.columns = ['timestamp', 'bpm', 'status']
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        # Display the data
        print("\n" + "="*70)
        print("HEART RATE RECORDS".center(70))
        print("="*70)
        
        # Group by date
        df['date'] = df['timestamp'].dt.date
        for date, group in df.groupby('date', sort=False):
            print(f"\n📅 {date.strftime('%A, %B %d, %Y')}")
            print("-" * 70)
            
            # Sort by time within each date
            group = group.sort_values('timestamp', ascending=False)
            
            for _, row in group.iterrows():
                time_str = row['timestamp'].strftime('%I:%M %p')
                status_emoji = '🔴' if row['status'] == 'HIGH' else '🟢'
                print(f"  {time_str} - {int(row['bpm'])} BPM {status_emoji} ({row['status']})")
        
        # Show summary
        print("\n" + "="*70)
        print("SUMMARY".center(70))
        print("="*70)
        print(f"Total readings: {len(df)}")
        print(f"Date range: {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}")
        print(f"Average BPM: {df['bpm'].mean():.1f}")
        
        high_readings = df[df['status'] == 'HIGH']
        if not high_readings.empty:
            print(f"\n⚠️  High BPM readings detected ({len(high_readings)}):")
            for _, row in high_readings.iterrows():
                print(f"  {row['timestamp'].strftime('%Y-%m-%d %I:%M %p')}: {int(row['bpm'])} BPM")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure 'heart_rate_data.xlsx' exists in the current directory.")

if __name__ == "__main__":
    view_heart_rate_data()
    input("\nPress Enter to exit...")
