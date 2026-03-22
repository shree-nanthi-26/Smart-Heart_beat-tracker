import pandas as pd
try:
    df = pd.read_excel('heart_rate_data.xlsx')
    print("Latest Heart Rate Data:")
    print("-" * 50)
    print(df[['timestamp', 'bpm', 'status']].to_string(index=False))
    print("
Summary:")
    print(f"Total readings: {len(df)}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Average BPM: {df['bpm'].mean():.1f}")
    print(f"Highest BPM: {df['bpm'].max()} ({df[df['bpm'] == df['bpm'].max()]['timestamp'].iloc[0]})")
    print(f"Lowest BPM: {df['bpm'].min()} ({df[df['bpm'] == df['bpm'].min()]['timestamp'].iloc[0]})")
except Exception as e:
    print(f"Error reading Excel file: {e}")