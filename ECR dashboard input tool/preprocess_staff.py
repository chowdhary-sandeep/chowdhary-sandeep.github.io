#!/usr/bin/env python3
"""
Preprocessing script for IIASA staff data.
Filters out non-current staff members and saves a clean Excel file.
"""

import pandas as pd
import os
from pathlib import Path

def preprocess_staff_data():
    """Preprocess staff data by filtering out non-current staff members"""
    
    # File paths
    input_file = 'staff_expertise_registered_in_MIS_2025-08-14.xlsx'
    output_file = 'staff_expertise_clean.xlsx'
    
    print(f"Loading staff data from: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"ERROR: Input file {input_file} not found!")
        return False
    
    try:
        # Read the original Excel file
        df = pd.read_excel(input_file, engine='openpyxl', sheet_name=0)
        print(f"Loaded {len(df)} rows from original file")
        
        # Check columns
        print(f"Columns: {list(df.columns)}")
        
        # Filter out rows where PERSON_MAIN_COST_CENTER contains "not current staff member"
        if 'PERSON_MAIN_COST_CENTER' in df.columns:
            original_count = len(df)
            df = df[~df['PERSON_MAIN_COST_CENTER'].astype(str).str.contains('not current staff member', case=False, na=False)]
            filtered_count = original_count - len(df)
            print(f"Filtered out {filtered_count} rows with 'not current staff member'")
            print(f"Remaining rows: {len(df)}")
        else:
            print("WARNING: PERSON_MAIN_COST_CENTER column not found, no filtering applied")
        
        # Filter out LANGUAGE expertise group skills (not important and clutter the graph)
        if 'EXPERTISE_GROUP' in df.columns:
            language_count = len(df[df['EXPERTISE_GROUP'].astype(str).str.contains('LANGUAGE', case=False, na=False)])
            df = df[~df['EXPERTISE_GROUP'].astype(str).str.contains('LANGUAGE', case=False, na=False)]
            print(f"Filtered out {language_count} rows with LANGUAGE expertise group")
            print(f"Remaining rows: {len(df)}")
        else:
            print("WARNING: EXPERTISE_GROUP column not found, no language filtering applied")
        
        # Save the cleaned data
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Saved cleaned data to: {output_file}")
        
        # Show some statistics
        if 'PERSON_NAME' in df.columns:
            unique_people = df['PERSON_NAME'].nunique()
            print(f"Unique people in cleaned data: {unique_people}")
        
        if 'EXPERTISE_NAME' in df.columns:
            unique_skills = df['EXPERTISE_NAME'].nunique()
            print(f"Unique skills in cleaned data: {unique_skills}")
        
        if 'EXPERTISE_GROUP' in df.columns:
            unique_groups = df['EXPERTISE_GROUP'].nunique()
            print(f"Unique expertise groups: {unique_groups}")
            print(f"Expertise groups: {sorted(df['EXPERTISE_GROUP'].unique())}")
        
        if 'PERSON_MAIN_COST_CENTER' in df.columns:
            unique_centers = df['PERSON_MAIN_COST_CENTER'].nunique()
            print(f"Unique cost centers: {unique_centers}")
            print(f"Cost centers: {sorted(df['PERSON_MAIN_COST_CENTER'].unique())}")
        
        return True
        
    except Exception as e:
        print(f"ERROR processing file: {e}")
        return False

if __name__ == '__main__':
    print("=== IIASA Staff Data Preprocessing ===")
    success = preprocess_staff_data()
    if success:
        print("✅ Preprocessing completed successfully!")
    else:
        print("❌ Preprocessing failed!")
