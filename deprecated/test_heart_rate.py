import pandas as pd
import time

# Sample data for testing
heart_data = [
    {"DateTime": "2025-09-30 10:00:00", "BPM": 88, "Alert": "NORMAL"},
    {"DateTime": "2025-09-30 10:05:00", "BPM": 92, "Alert": "HIGH"},
    {"DateTime": "2025-09-30 10:10:00", "BPM": 85, "Alert": "NORMAL"},
    {"DateTime": "2025-09-30 10:15:00", "BPM": 95, "Alert": "HIGH"},
    {"DateTime": "2025-09-30 10:20:00", "BPM": 89, "Alert": "NORMAL"},
]

# Create DataFrame
df = pd.DataFrame(heart_data)

# Save to Excel
df.to_excel("test_heart_rate_data.xlsx", index=False)
print("Test data saved to test_heart_rate_data.xlsx")

# Print summary
high_readings = df[df['Alert'] == 'HIGH']
print("\n" + "="*60)
print("TEST HEART RATE MONITORING SUMMARY")
print("="*60)
print(f"Total readings: {len(df)}")
print(f"High heart rate readings: {len(high_readings)}")

if not high_readings.empty:
    print("\nHigh heart rate alerts:")
    print("-"*60)
    for _, row in high_readings.iterrows():
        print(f"• {row['DateTime']}: {row['BPM']} BPM")
else:
    print("\n✅ No high heart rate readings detected.")

print("\n" + "="*60)
print("Sample data:")
print("-"*60)
print(df)
print("="*60)
