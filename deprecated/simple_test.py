import os
import time
import pandas as pd
from datetime import datetime
import asyncio

async def main():
    print("Starting simplified heart rate monitor...")
    
    # Create some dummy data
    heart_data = []
    for i in range(5):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bpm = 70 + i * 5  # Simulate increasing heart rate
        heart_data.append({
            "DateTime": now,
            "BPM": bpm,
            "Alert": "HIGH" if bpm > 85 else "NORMAL"
        })
        print(f"Recorded {bpm} BPM at {now}")
        await asyncio.sleep(1)  # Wait 1 second between readings
    
    # Save to CSV
    df = pd.DataFrame(heart_data)
    df.to_csv("test_heart_rate.csv", index=False)
    print("\nTest completed! Data saved to test_heart_rate.csv")

def run_async():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'loop' in locals():
            loop.close()
        input("Press Enter to exit...")

if __name__ == "__main__":
    run_async()
