import pandas as pd
from datetime import datetime

# Read the existing Excel file
try:
    df = pd.read_excel('heart_rate_data.xlsx')
    print("Current data in Excel file:")
    print(df.to_string())
    
    # Check if we need to clean up the data
    if 'Unnamed: 0' in df.columns:
        print("\nCleaning up the Excel file...")
        
        # Keep only relevant columns
        if 'timestamp' in df.columns:
            # This is the new format
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp', 'bpm', 'status']].copy()
            df['date'] = df['timestamp'].dt.date
            df['time'] = df['timestamp'].dt.time
        else:
            # This is the old format
            df = df[['DateTime', 'BPM', 'Alert']].copy()
            df.columns = ['timestamp', 'bpm', 'status']
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['time'] = df['timestamp'].dt.time
        
        # Remove duplicates and sort
        df = df.drop_duplicates('timestamp').sort_values('timestamp', ascending=False)
        
        # Save the cleaned data
        df.to_excel('heart_rate_data_cleaned.xlsx', index=False)
        print("\n✅ Cleaned data saved to 'heart_rate_data_cleaned.xlsx'")
        print("\nSample of cleaned data:")
        print(df.head().to_string())
    
    else:
        print("\nThe Excel file is already in the correct format.")
        
except Exception as e:
    print(f"\n❌ Error processing Excel file: {e}")

# Create a script to view the data
with open('view_data.py', 'w') as f:
    f.write("""import pandas as pd
try:
    df = pd.read_excel('heart_rate_data.xlsx')
    print("Latest Heart Rate Data:")
    print("-" * 50)
    print(df[['timestamp', 'bpm', 'status']].to_string(index=False))
    print("\nSummary:")
    print(f"Total readings: {len(df)}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Average BPM: {df['bpm'].mean():.1f}")
    print(f"Highest BPM: {df['bpm'].max()} ({df[df['bpm'] == df['bpm'].max()]['timestamp'].iloc[0]})")
    print(f"Lowest BPM: {df['bpm'].min()} ({df[df['bpm'] == df['bpm'].min()]['timestamp'].iloc[0]})")
except Exception as e:
    print(f"Error reading Excel file: {e}")""")

print("\nYou can view your data by running: python view_data.py")
