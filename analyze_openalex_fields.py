#!/usr/bin/env python3
"""
OpenAlex Field Analysis Script

This script analyzes the OpenAlex topic mapping table Excel file
and extracts unique values from the field_name column, plus searches
for "climate" in keywords and analyzes other columns for those rows.
All results are saved as Excel files with comprehensive analysis.
"""

import pandas as pd
import sys
from pathlib import Path

def analyze_openalex_fields(excel_file_path):
    """
    Analyze the OpenAlex Excel file and extract unique field_name values.
    
    Args:
        excel_file_path (str): Path to the Excel file
        
    Returns:
        list: Unique values from field_name column
    """
    try:
        # Read the Excel file
        print(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # Display basic information about the dataset
        print(f"\nDataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check if field_name column exists
        if 'field_name' not in df.columns:
            print("\nError: 'field_name' column not found!")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        # Get unique values from field_name column
        unique_fields = df['field_name'].unique()
        
        # Remove NaN values and sort
        unique_fields = sorted([field for field in unique_fields if pd.notna(field)])
        
        print(f"\nFound {len(unique_fields)} unique field_name values:")
        print("-" * 50)
        
        for i, field in enumerate(unique_fields, 1):
            print(f"{i:3d}. {field}")
        
        # Display some statistics
        print(f"\nStatistics:")
        print(f"Total rows: {len(df)}")
        print(f"Unique field_name values: {len(unique_fields)}")
        
        # Count occurrences of each field_name
        field_counts = df['field_name'].value_counts()
        print(f"\nTop 10 most common field_name values:")
        print("-" * 50)
        for field, count in field_counts.head(10).items():
            print(f"{field}: {count} occurrences")
        
        return unique_fields, df
        
    except FileNotFoundError:
        print(f"Error: File '{excel_file_path}' not found!")
        return None, None
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None, None

def analyze_climate_keywords(df):
    """
    Search for "climate" in keywords column and analyze other columns for those rows.
    
    Args:
        df (DataFrame): The loaded DataFrame
    """
    if 'keywords' not in df.columns:
        print("\nError: 'keywords' column not found!")
        return None
    
    print(f"\n{'='*60}")
    print("CLIMATE KEYWORDS ANALYSIS")
    print(f"{'='*60}")
    
    # Search for rows containing "climate" in keywords (case-insensitive)
    climate_mask = df['keywords'].str.contains('climate', case=False, na=False)
    climate_rows = df[climate_mask]
    
    print(f"\nFound {len(climate_rows)} rows containing 'climate' in keywords")
    
    if len(climate_rows) == 0:
        print("No rows found with 'climate' in keywords.")
        return None
    
    # Analyze each column for climate-related rows
    print(f"\nColumn analysis for climate-related rows:")
    print("-" * 50)
    
    column_analysis = {}
    
    for column in df.columns:
        if column == 'keywords':
            continue  # Skip keywords column as we already filtered by it
        
        # Get unique values and counts for this column in climate rows
        unique_values = climate_rows[column].value_counts()
        column_analysis[column] = unique_values
        
        print(f"\n{column.upper()} (Top 10 most common):")
        print("-" * 30)
        
        if len(unique_values) > 0:
            for value, count in unique_values.head(10).items():
                if pd.notna(value):
                    print(f"  {value}: {count}")
                else:
                    print(f"  [NULL/NaN]: {count}")
        else:
            print("  No data available")
    
    # Show some sample climate-related rows
    print(f"\nSample climate-related topics (first 5):")
    print("-" * 50)
    for idx, row in climate_rows.head(5).iterrows():
        print(f"\nTopic: {row.get('topic_name', 'N/A')}")
        print(f"Field: {row.get('field_name', 'N/A')}")
        print(f"Keywords: {row.get('keywords', 'N/A')}")
        print(f"Summary: {str(row.get('summary', 'N/A'))[:100]}...")
    
    return climate_rows, column_analysis

def save_results_to_excel(df, unique_fields, climate_rows, column_analysis):
    """
    Save all analysis results to Excel files with multiple sheets.
    
    Args:
        df (DataFrame): Complete dataset
        unique_fields (list): Unique field names
        climate_rows (DataFrame): Climate-related rows
        column_analysis (dict): Column analysis results
    """
    print(f"\n{'='*60}")
    print("SAVING RESULTS TO EXCEL FILES")
    print(f"{'='*60}")
    
    # 1. Save complete dataset analysis
    with pd.ExcelWriter('OpenAlex_Complete_Analysis.xlsx', engine='openpyxl') as writer:
        
        # Sheet 1: Complete Dataset
        df.to_excel(writer, sheet_name='Complete_Dataset', index=False)
        print("✓ Complete dataset saved to 'Complete_Dataset' sheet")
        
        # Sheet 2: Field Analysis
        field_counts = df['field_name'].value_counts().reset_index()
        field_counts.columns = ['Field Name', 'Count']
        field_counts['Percentage'] = (field_counts['Count'] / len(df) * 100).round(2)
        field_counts.to_excel(writer, sheet_name='Field_Analysis', index=False)
        print("✓ Field analysis saved to 'Field_Analysis' sheet")
        
        # Sheet 3: Subfield Analysis
        if 'subfield_name' in df.columns:
            subfield_counts = df['subfield_name'].value_counts().reset_index()
            subfield_counts.columns = ['Subfield Name', 'Count']
            subfield_counts['Percentage'] = (subfield_counts['Count'] / len(df) * 100).round(2)
            subfield_counts.to_excel(writer, sheet_name='Subfield_Analysis', index=False)
            print("✓ Subfield analysis saved to 'Subfield_Analysis' sheet")
        
        # Sheet 4: Domain Analysis
        if 'domain_name' in df.columns:
            domain_counts = df['domain_name'].value_counts().reset_index()
            domain_counts.columns = ['Domain Name', 'Count']
            domain_counts['Percentage'] = (domain_counts['Count'] / len(df) * 100).round(2)
            domain_counts.to_excel(writer, sheet_name='Domain_Analysis', index=False)
            print("✓ Domain analysis saved to 'Domain_Analysis' sheet")
        
        # Sheet 5: Topic Analysis
        if 'topic_name' in df.columns:
            topic_counts = df['topic_name'].value_counts().reset_index()
            topic_counts.columns = ['Topic Name', 'Count']
            topic_counts['Percentage'] = (topic_counts['Count'] / len(df) * 100).round(2)
            topic_counts.to_excel(writer, sheet_name='Topic_Analysis', index=False)
            print("✓ Topic analysis saved to 'Topic_Analysis' sheet")
    
    # 2. Save climate-specific analysis
    if climate_rows is not None and len(climate_rows) > 0:
        with pd.ExcelWriter('OpenAlex_Climate_Analysis.xlsx', engine='openpyxl') as writer:
            
            # Sheet 1: Climate Topics
            climate_rows.to_excel(writer, sheet_name='Climate_Topics', index=False)
            print("✓ Climate topics saved to 'Climate_Topics' sheet")
            
            # Sheet 2: Climate Field Analysis
            climate_field_counts = climate_rows['field_name'].value_counts().reset_index()
            climate_field_counts.columns = ['Field Name', 'Count']
            climate_field_counts['Percentage'] = (climate_field_counts['Count'] / len(climate_rows) * 100).round(2)
            climate_field_counts.to_excel(writer, sheet_name='Climate_Field_Analysis', index=False)
            print("✓ Climate field analysis saved to 'Climate_Field_Analysis' sheet")
            
            # Sheet 3: Climate Subfield Analysis
            if 'subfield_name' in climate_rows.columns:
                climate_subfield_counts = climate_rows['subfield_name'].value_counts().reset_index()
                climate_subfield_counts.columns = ['Subfield Name', 'Count']
                climate_subfield_counts['Percentage'] = (climate_subfield_counts['Count'] / len(climate_rows) * 100).round(2)
                climate_subfield_counts.to_excel(writer, sheet_name='Climate_Subfield_Analysis', index=False)
                print("✓ Climate subfield analysis saved to 'Climate_Subfield_Analysis' sheet")
            
            # Sheet 4: Climate Domain Analysis
            if 'domain_name' in climate_rows.columns:
                climate_domain_counts = climate_rows['domain_name'].value_counts().reset_index()
                climate_domain_counts.columns = ['Domain Name', 'Count']
                climate_domain_counts['Percentage'] = (climate_domain_counts['Count'] / len(climate_rows) * 100).round(2)
                climate_domain_counts.to_excel(writer, sheet_name='Climate_Domain_Analysis', index=False)
                print("✓ Climate domain analysis saved to 'Climate_Domain_Analysis' sheet")
            
            # Sheet 5: Column Analysis Summary
            column_summary = []
            for column, value_counts in column_analysis.items():
                for value, count in value_counts.head(20).items():  # Top 20 for each column
                    if pd.notna(value):
                        column_summary.append({
                            'Column': column,
                            'Value': value,
                            'Count': count,
                            'Percentage': round((count / len(climate_rows) * 100), 2)
                        })
            
            if column_summary:
                column_summary_df = pd.DataFrame(column_summary)
                column_summary_df.to_excel(writer, sheet_name='Column_Analysis_Summary', index=False)
                print("✓ Column analysis summary saved to 'Column_Analysis_Summary' sheet")
    
    print(f"\nAll results saved to Excel files:")
    print("• OpenAlex_Complete_Analysis.xlsx - Complete dataset analysis")
    if climate_rows is not None and len(climate_rows) > 0:
        print("• OpenAlex_Climate_Analysis.xlsx - Climate-specific analysis")

def main():
    """Main function to run the analysis."""
    # Default file path
    default_file = "OpenAlex_topic_mapping_table.xlsx"
    
    # Check if file path is provided as command line argument
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        excel_file = default_file
    
    # Check if file exists
    if not Path(excel_file).exists():
        print(f"Error: File '{excel_file}' not found!")
        print(f"Please provide a valid Excel file path as a command line argument.")
        print(f"Usage: python analyze_openalex_fields.py [excel_file_path]")
        return
    
    # Run the analysis
    unique_fields, df = analyze_openalex_fields(excel_file)
    
    if unique_fields and df is not None:
        # Analyze climate keywords
        climate_results = analyze_climate_keywords(df)
        
        if climate_results:
            climate_rows, column_analysis = climate_results
        else:
            climate_rows, column_analysis = None, None
        
        # Save all results to Excel files
        save_results_to_excel(df, unique_fields, climate_rows, column_analysis)

if __name__ == "__main__":
    main()
