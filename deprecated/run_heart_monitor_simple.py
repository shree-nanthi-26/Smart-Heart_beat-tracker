import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load the heart rate data
try:
    df = pd.read_csv('heart_rate_data.csv')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    print("Successfully loaded heart rate data:")
    print(df.head())
    
    # Simple visualization
    plt.figure(figsize=(12, 6))
    plt.plot(df['DateTime'], df['BPM'], 'r-', label='Heart Rate (BPM)')
    plt.axhline(y=99, color='g', linestyle='--', label='Threshold (99 BPM)')
    plt.title('Heart Rate Over Time')
    plt.xlabel('Time')
    plt.ylabel('BPM')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # Print latest reading
    latest = df.iloc[-1]
    print(f"\nLatest Reading:")
    print(f"Time: {latest['DateTime']}")
    print(f"Heart Rate: {latest['BPM']} BPM")
    print(f"Status: {latest['Alert']}")
    
    if latest['BPM'] > 99:
        print("\n⚠️  WARNING: High heart rate detected!")
        
except Exception as e:
    print(f"Error: {e}")
    print("Make sure 'heart_rate_data.csv' exists in the current directory.")

print("\nPress Enter to exit...")
input()
