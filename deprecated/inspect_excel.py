import pandas as pd

print("Inspecting heart_rate_data.xlsx...")

# Read the Excel file
try:
    df = pd.read_excel('heart_rate_data.xlsx')
    
    print("\nColumns in the file:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nFirst 3 rows of data:")
    print(df.head(3).to_string())
    
    print("\nLast 3 rows of data:")
    print(df.tail(3).to_string())
    
except Exception as e:
    print(f"\n❌ Error reading file: {e}")
