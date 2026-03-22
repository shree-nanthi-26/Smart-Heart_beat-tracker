import pandas as pd
import requests

def main():
    try:
        # Read the Excel file
        df = pd.read_excel('heart_rate_data.xlsx')
        print("Successfully read the Excel file.")
        
        # Print column names for debugging
        print("\nColumns in the file:")
        for i, col in enumerate(df.columns):
            print(f"{i+1}. {col}")
            
        # Try to find date and BPM columns (case insensitive)
        date_col = next((col for col in df.columns if 'date' in str(col).lower()), None)
        bpm_col = next((col for col in df.columns if 'bpm' in str(col).lower()), None)
        
        if not date_col or not bpm_col:
            print("\nError: Could not find required columns. Please check your data file.")
            return
            
        print(f"\nUsing columns: Date='{date_col}', BPM='{bpm_col}'")
        
        # Convert date column to datetime
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Group by date and show basic stats
        print("\nDaily Summary:")
        print("-" * 50)
        
        for date, group in df.groupby(df[date_col].dt.date):
            print(f"\n📅 Date: {date}")
            print(f"   • Readings: {len(group)}")
            print(f"   • Avg BPM: {group[bpm_col].mean():.1f}")
            print(f"   • Min BPM: {group[bpm_col].min()}")
            print(f"   • Max BPM: {group[bpm_col].max()}")
            
            # Show high readings
            high_readings = group[group[bpm_col] > 85]
            if len(high_readings) > 0:
                print(f"   • High readings (>85 BPM): {len(high_readings)}")
                for _, row in high_readings.head(5).iterrows():
                    print(f"     - {row[date_col].strftime('%H:%M')}: {row[bpm_col]} BPM")
                if len(high_readings) > 5:
                    print(f"     - ... and {len(high_readings) - 5} more")
            else:
                print("   • No high readings (>85 BPM)")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    print("Analyzing heart rate data...\n")
    main()
