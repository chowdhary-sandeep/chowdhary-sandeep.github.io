#!/usr/bin/env python3
"""
OpenAlex Climate Topics API Analysis Script

This script reads the climate topics from our analysis, queries the OpenAlex API
to get paper counts for each topic, and saves the results to Excel files.
"""

import pandas as pd
import requests
import time
from pathlib import Path
import json
from datetime import datetime

# Reuse a single HTTP session and set polite headers
SESSION = requests.Session()
DEFAULT_HEADERS = {
    'User-Agent': 'openalex-climate-analysis; mailto:chowdhary@iiasa.ac.at',
    'Accept': 'application/json'
}

def load_climate_topics():
    """
    Load climate topics from our Excel analysis file.
    
    Returns:
        DataFrame: Climate topics with topic_id and topic_name
    """
    try:
        # Read the climate analysis Excel file
        climate_df = pd.read_excel('OpenAlex_Climate_Analysis.xlsx', sheet_name='Climate_Topics')
        print(f"Loaded {len(climate_df)} climate topics from Excel file")
        return climate_df[['topic_id', 'topic_name']].drop_duplicates()
    except Exception as e:
        print(f"Error loading climate topics: {e}")
        return None

def search_topic_by_name(topic_name: str, max_retries: int = 3, delay: float = 1.0):
    """
    Search OpenAlex Topics by display name and return the best match.
    """
    base_url = "https://api.openalex.org/topics"
    params = {
        'search': topic_name,
        'per-page': 1,
        'mailto': 'researcher@example.com'
    }
    for attempt in range(max_retries):
        try:
            print(f"Searching topic by name: '{topic_name}' (attempt {attempt + 1})")
            response = SESSION.get(base_url, params=params, headers=DEFAULT_HEADERS, timeout=30)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                if results:
                    top = results[0]
                    return {
                        'matched_topic_openalex_id': top.get('id'),
                        'matched_topic_display_name': top.get('display_name'),
                        'works_count': top.get('works_count', 0)
                    }
                return None
            elif response.status_code == 429:
                time.sleep(delay * (attempt + 1))
            else:
                print(f"Search API error {response.status_code}: {response.text}")
                time.sleep(delay)
        except Exception as e:
            print(f"Search request failed for '{topic_name}': {e}")
            time.sleep(delay)
    return None

def query_openalex_api(topic_id, topic_name=None, max_retries=3, delay=1):
    """
    Query OpenAlex API Topics endpoint for a specific topic to get works_count.
    
    Args:
        topic_id (str | int): The OpenAlex numeric topic ID (without the leading 'T')
        max_retries (int): Maximum number of retry attempts
        delay (float): Delay between requests in seconds
    
    Returns:
        dict: { topic_id, paper_count, query_time } or None if failed
    """
    base_url = "https://api.openalex.org/topics"
    url = f"{base_url}/T{topic_id}"
    params = {
        'mailto': 'researcher@example.com'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"Querying topic {topic_id} (attempt {attempt + 1})")
            print(f"URL: {url}")
            response = SESSION.get(url, params=params, headers=DEFAULT_HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'topic_id': topic_id,
                    'paper_count': data.get('works_count', 0),
                    'query_time': datetime.now().isoformat()
                }
            elif response.status_code == 429:  # Rate limit
                print(f"Rate limited. Waiting {delay * (attempt + 1)} seconds...")
                time.sleep(delay * (attempt + 1))
            else:
                # If the topic id is invalid (400), try falling back to name search if provided
                print(f"API error {response.status_code}: {response.text}")
                if response.status_code == 400 and topic_name:
                    fallback = search_topic_by_name(topic_name, max_retries=1, delay=delay)
                    if fallback:
                        return {
                            'topic_id': topic_id,
                            'paper_count': fallback['works_count'],
                            'query_time': datetime.now().isoformat(),
                            'matched_topic_openalex_id': fallback['matched_topic_openalex_id'],
                            'matched_topic_display_name': fallback['matched_topic_display_name']
                        }
                # As a final fallback for some servers, try without params
                if response.status_code == 400:
                    try:
                        bare = SESSION.get(url, headers=DEFAULT_HEADERS, timeout=30)
                        if bare.status_code == 200:
                            data = bare.json()
                            return {
                                'topic_id': topic_id,
                                'paper_count': data.get('works_count', 0),
                                'query_time': datetime.now().isoformat()
                            }
                    except Exception:
                        pass
                time.sleep(delay)
                
        except Exception as e:
            print(f"Request failed for topic {topic_id}: {e}")
            time.sleep(delay)
    
    print(f"Failed to get data for topic {topic_id} after {max_retries} attempts")
    return None

def get_all_paper_counts(climate_topics_df):
    """
    Get paper counts for all climate topics from OpenAlex API.
    
    Args:
        climate_topics_df (DataFrame): DataFrame with topic_id and topic_name
    
    Returns:
        DataFrame: Climate topics with paper counts
    """
    results = []
    total_topics = len(climate_topics_df)
    print(f"Querying OpenAlex API for {total_topics} climate topics...")
    
    # Batch query using topics list endpoint with ids.openalex filter
    batch_size = 40
    topic_rows = climate_topics_df[['topic_id', 'topic_name']].drop_duplicates().reset_index(drop=True)
    
    for start in range(0, total_topics, batch_size):
        end = min(start + batch_size, total_topics)
        batch = topic_rows.iloc[start:end]
        print(f"\nBatch {start+1}-{end} of {total_topics}")
        
        # Build ids.openalex filter
        id_uris = [f"https://openalex.org/T{int(tid)}" for tid in batch['topic_id']]
        filter_str = "|".join(id_uris)
        params = {
            'filter': f'ids.openalex:{filter_str}',
            'per-page': len(id_uris),
            'mailto': 'chowdhary@iiasa.ac.at'
        }
        try:
            resp = SESSION.get('https://api.openalex.org/topics', params=params, headers=DEFAULT_HEADERS, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                results_list = data.get('results', [])
                # Map URI -> works_count and display_name
                uri_to_info = { r.get('id'): (r.get('works_count', 0), r.get('display_name')) for r in results_list }
                # Populate results preserving original order
                for _, row in batch.iterrows():
                    uri = f"https://openalex.org/T{int(row['topic_id'])}"
                    works_count, disp = uri_to_info.get(uri, (None, None))
                    if works_count is None:
                        # Fallback to single query
                        api_result = query_openalex_api(row['topic_id'], topic_name=row['topic_name'])
                        if api_result:
                            results.append({
                                'topic_id': row['topic_id'],
                                'topic_name': row['topic_name'],
                                'paper_count': api_result['paper_count'],
                                'query_time': api_result['query_time']
                            })
                        else:
                            results.append({
                                'topic_id': row['topic_id'],
                                'topic_name': row['topic_name'],
                                'paper_count': 0,
                                'query_time': datetime.now().isoformat()
                            })
                    else:
                        results.append({
                            'topic_id': row['topic_id'],
                            'topic_name': row['topic_name'],
                            'paper_count': int(works_count),
                            'query_time': datetime.now().isoformat()
                        })
            else:
                print(f"Batch API error {resp.status_code}: {resp.text[:200]}")
                # Fallback: per-topic queries for this batch
                for _, row in batch.iterrows():
                    api_result = query_openalex_api(row['topic_id'], topic_name=row['topic_name'])
                    if api_result:
                        results.append({
                            'topic_id': row['topic_id'],
                            'topic_name': row['topic_name'],
                            'paper_count': api_result['paper_count'],
                            'query_time': api_result['query_time']
                        })
                    else:
                        results.append({
                            'topic_id': row['topic_id'],
                            'topic_name': row['topic_name'],
                            'paper_count': 0,
                            'query_time': datetime.now().isoformat()
                        })
        except Exception as e:
            print(f"Batch request failed: {e}")
            # Fallback: per-topic queries for this batch
            for _, row in batch.iterrows():
                api_result = query_openalex_api(row['topic_id'], topic_name=row['topic_name'])
                if api_result:
                    results.append({
                        'topic_id': row['topic_id'],
                        'topic_name': row['topic_name'],
                        'paper_count': api_result['paper_count'],
                        'query_time': api_result['query_time']
                    })
                else:
                    results.append({
                        'topic_id': row['topic_id'],
                        'topic_name': row['topic_name'],
                        'paper_count': 0,
                        'query_time': datetime.now().isoformat()
                    })
        # Gentle delay between batches
        time.sleep(0.5)
    
    return pd.DataFrame(results)

def calculate_summary_stats(paper_counts_df):
    """
    Calculate summary statistics for the paper counts.
    
    Args:
        paper_counts_df (DataFrame): DataFrame with topic names and paper counts
        
    Returns:
        dict: Summary statistics
    """
    total_papers = paper_counts_df['paper_count'].sum()
    mean_papers = paper_counts_df['paper_count'].mean()
    median_papers = paper_counts_df['paper_count'].median()
    max_papers = paper_counts_df['paper_count'].max()
    min_papers = paper_counts_df['paper_count'].min()
    std_papers = paper_counts_df['paper_count'].std()
    
    # Find topic with most papers
    max_topic = paper_counts_df.loc[paper_counts_df['paper_count'].idxmax(), 'topic_name']
    
    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS")
    print(f"{'='*60}")
    print(f"Total Climate Topics Analyzed: {len(paper_counts_df):,}")
    print(f"Total Papers Across All Topics: {total_papers:,}")
    print(f"Mean papers per topic: {mean_papers:.1f}")
    print(f"Median papers per topic: {median_papers:.0f}")
    print(f"Standard deviation: {std_papers:.1f}")
    print(f"Maximum papers: {max_papers:,}")
    print(f"Most researched topic: {max_topic}")
    print(f"Minimum papers: {min_papers:,}")
    
    # Show top 10 topics
    print(f"\nTop 10 Topics by Paper Count:")
    print("-" * 80)
    top_10 = paper_counts_df.nlargest(10, 'paper_count')
    for i, (idx, row) in enumerate(top_10.iterrows(), 1):
        print(f"{i:2d}. {row['topic_name'][:65]:65} {row['paper_count']:>8,} papers")
    
    return {
        'total_topics': len(paper_counts_df),
        'total_papers': total_papers,
        'mean_papers': mean_papers,
        'median_papers': median_papers,
        'std_papers': std_papers,
        'max_papers': max_papers,
        'min_papers': min_papers,
        'max_topic': max_topic
    }

def save_results(paper_counts_df):
    """
    Save the API results to Excel and CSV files.
    
    Args:
        paper_counts_df (DataFrame): Results with paper counts
    """
    # Save to Excel
    excel_path = Path('Figures') / 'climate_topics_paper_counts.xlsx'
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Sort by paper count descending
        sorted_results = paper_counts_df.sort_values('paper_count', ascending=False)
        sorted_results.to_excel(writer, sheet_name='Climate_Topic_Counts', index=False)
        
        # Add summary statistics
        summary_stats = pd.DataFrame({
            'Statistic': ['Total Topics', 'Total Papers', 'Mean Papers/Topic', 
                         'Median Papers/Topic', 'Max Papers', 'Min Papers'],
            'Value': [
                len(paper_counts_df),
                paper_counts_df['paper_count'].sum(),
                round(paper_counts_df['paper_count'].mean(), 1),
                paper_counts_df['paper_count'].median(),
                paper_counts_df['paper_count'].max(),
                paper_counts_df['paper_count'].min()
            ]
        })
        summary_stats.to_excel(writer, sheet_name='Summary_Statistics', index=False)
    
    print(f"Results saved to: {excel_path}")
    
    # Also save as CSV for easy access
    csv_path = Path('Figures') / 'climate_topics_paper_counts.csv'
    paper_counts_df.sort_values('paper_count', ascending=False).to_csv(csv_path, index=False)
    print(f"Results also saved to: {csv_path}")

def main():
    """Main function to run the complete analysis."""
    print("="*60)
    print("OPENALEX CLIMATE TOPICS API ANALYSIS")
    print("="*60)
    
    # Load climate topics from our previous analysis
    climate_topics = load_climate_topics()
    if climate_topics is None:
        print("Failed to load climate topics. Exiting.")
        return
    
    print(f"\nFound {len(climate_topics)} unique climate topics to analyze")
    
    # Test with first 5 topics to check API format
    print("\nTesting API with first 5 topics...")
    test_topics = climate_topics.head(5)
    test_results = get_all_paper_counts(test_topics)
    
    if len(test_results) == 0 or all(result['paper_count'] == 0 for _, result in test_results.iterrows()):
        print("API test failed. Please check the API format.")
        return
    
    print("API test successful! Proceeding with all topics...")
    
    # Get paper counts from OpenAlex API for all topics
    print(f"\nQuerying OpenAlex API for all {len(climate_topics)} topics...")
    paper_counts = get_all_paper_counts(climate_topics)
    
    if len(paper_counts) == 0:
        print("No data retrieved from API. Exiting.")
        return
    
    print(f"\nSuccessfully retrieved data for {len(paper_counts)} topics")
    
    # Calculate and display summary statistics
    print("\nCalculating summary statistics...")
    stats = calculate_summary_stats(paper_counts)
    
    # Save results
    print("\nSaving results...")
    save_results(paper_counts)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print(f"Total papers across all climate topics: {paper_counts['paper_count'].sum():,}")
    print(f"Average papers per topic: {paper_counts['paper_count'].mean():.1f}")
    print(f"Most researched topic: {paper_counts.loc[paper_counts['paper_count'].idxmax(), 'topic_name']}")
    print(f"Papers in most researched topic: {paper_counts['paper_count'].max():,}")

if __name__ == "__main__":
    main()
