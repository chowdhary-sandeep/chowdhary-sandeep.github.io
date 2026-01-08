import pandas as pd
import os

STAFF_EXCEL_PATH = 'staff_expertise_registered_in_MIS_2025-08-14.xlsx'

print(f"Loading staff expertise from: {STAFF_EXCEL_PATH}")
if not os.path.exists(STAFF_EXCEL_PATH): 
    print("Staff file does not exist")
    exit(1)

try:
    # Try to read the first sheet only
    df = pd.read_excel(STAFF_EXCEL_PATH, engine='openpyxl', sheet_name=0)
    print(f"Loaded sheet with {len(df)} rows")
except Exception as e:
    print(f"Error reading staff file: {e}")
    exit(1)

if df is None or df.empty:
    print("Staff file is empty")
    exit(1)

df = df.fillna('')
df.columns = [str(c).strip() for c in df.columns]
print(f"Columns in staff file: {list(df.columns)}")

# Show first few rows
print("\nFirst 5 rows:")
print(df.head())

# Look for specific columns - exact matching first, then flexible
person_col = None
expertise_col = None

for col in df.columns:
    col_lower = col.lower().strip()
    print(f"Checking column: '{col}' (lowercase: '{col_lower}')")
    
    # Exact match first for PERSON_NAME
    if col_lower == 'person_name':
        person_col = col
        print(f"Found person column (exact match): '{col}'")
    
    # Exact match first for EXPERTISE_NAME
    if col_lower == 'expertise_name':
        expertise_col = col
        print(f"Found expertise column (exact match): '{col}'")

# If exact matches not found, try flexible matching
if not person_col:
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'person' in col_lower and 'name' in col_lower:
            person_col = col
            print(f"Found person column (flexible match): '{col}'")
            break

if not expertise_col:
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'expertise' in col_lower and 'name' in col_lower:
            expertise_col = col
            print(f"Found expertise column (flexible match): '{col}'")
            break

if not person_col or not expertise_col:
    print(f"ERROR: Could not find required columns!")
    print(f"Looking for columns containing 'person' and 'expertise'")
    print(f"Available columns: {list(df.columns)}")
    exit(1)

print(f"\nUsing columns: person='{person_col}', expertise='{expertise_col}'")

# Show some sample data
print(f"\nSample data from these columns:")
for i in range(min(10, len(df))):
    person = str(df.iloc[i][person_col]).strip()
    expertise = str(df.iloc[i][expertise_col]).strip()
    print(f"Row {i}: Person='{person}', Expertise='{expertise}'")
