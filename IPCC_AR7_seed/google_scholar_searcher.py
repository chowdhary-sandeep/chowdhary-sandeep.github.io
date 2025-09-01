#!/usr/bin/env python3
"""
Google Scholar Search Module for IPCC AR7 Seed Papers
This module searches Google Scholar for each topic and extracts paper metadata.
"""

import time
import json
import re
from typing import List, Dict, Any, Optional
import requests
from urllib.parse import quote_plus
import random

class GoogleScholarSearcher:
    def __init__(self):
        self.base_url = "https://scholar.google.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.delay_range = (2, 5)  # Random delay between requests
    
    def search_papers(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search Google Scholar for papers matching the query.
        Returns list of paper metadata including citation counts.
        """
        try:
            # Use a simpler query approach that's less likely to be blocked
            # Just use the main query without additional constraints
            formatted_query = query
            encoded_query = quote_plus(formatted_query)
            search_url = f"{self.base_url}/scholar?q={encoded_query}&hl=en"
            
            print(f"Searching: {formatted_query}")
            print(f"URL: {search_url}")
            
            # Update headers to better mimic a real browser
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            })
            
            # Add random delay to avoid rate limiting
            delay = random.uniform(*self.delay_range)
            print(f"Waiting {delay:.1f} seconds...")
            time.sleep(delay)
            
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code != 200:
                print(f"HTTP Error {response.status_code}: {response.text[:200]}")
                return []
            
            print(f"Response length: {len(response.text)} characters")
            
            # Save a sample of the HTML for debugging
            with open('google_scholar_sample.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:10000])  # Save first 10000 characters
            print("  Saved HTML sample to google_scholar_sample.html")
            
            # Parse HTML response to extract paper information
            papers = self._parse_search_results(response.text, query, max_results)
            
            print(f"Found {len(papers)} papers")
            return papers
            
        except Exception as e:
            print(f"Error searching for '{query}': {str(e)}")
            return []
    
    def _parse_search_results(self, html_content: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Parse HTML content from Google Scholar search results.
        Extract paper title, authors, publication info, and citation count.
        """
        papers = []
        
        # Debug: Look for common Google Scholar patterns in the HTML
        print("  Debug: Examining HTML structure...")
        if 'gs_rt' in html_content:
            print("    Found 'gs_rt' in HTML")
        if 'gs_a' in html_content:
            print("    Found 'gs_a' in HTML")
        if 'Cited by' in html_content:
            print("    Found 'Cited by' in HTML")
        if 'h3' in html_content:
            print("    Found 'h3' tags in HTML")
        
        # Look for any text that might be a paper title
        title_candidates = re.findall(r'<h3[^>]*>(.*?)</h3>', html_content, re.DOTALL | re.IGNORECASE)
        print(f"    Raw h3 tags found: {len(title_candidates)}")
        if title_candidates:
            print(f"    First h3 content: {title_candidates[0][:100]}...")
        
        # Look for gs_rt divs directly
        gs_rt_divs = re.findall(r'<div[^>]*class="gs_rt"[^>]*>(.*?)</div>', html_content, re.DOTALL | re.IGNORECASE)
        print(f"    gs_rt divs found: {len(gs_rt_divs)}")
        if gs_rt_divs:
            print(f"    First gs_rt div content: {gs_rt_divs[0][:100]}...")
        
        # Look for any div tags
        all_divs = re.findall(r'<div[^>]*>(.*?)</div>', html_content, re.DOTALL | re.IGNORECASE)
        print(f"    Total div tags found: {len(all_divs)}")
        
        # Look for any text that looks like a paper title
        potential_titles = []
        for div in all_divs[:20]:  # Check first 20 divs
            clean_div = self._clean_text(div)
            if len(clean_div) > 20 and len(clean_div) < 200:
                if any(word in clean_div.lower() for word in ['climate', 'change', 'mitigation', 'development', 'policy']):
                    potential_titles.append(clean_div)
        
        print(f"    Potential title candidates: {len(potential_titles)}")
        if potential_titles:
            print(f"    First candidate: {potential_titles[0][:80]}...")
        
        # Multiple patterns to try for different Google Scholar layouts
        patterns = [
            # Pattern 1: Modern Google Scholar layout with gs_rt class
            {
                'paper': r'<h3 class="gs_rt">.*?<a.*?>(.*?)</a>.*?</h3>',
                'author': r'<div class="gs_a">(.*?)</div>',
                'citation': r'Cited by (\d+)'
            },
            # Pattern 2: Alternative layout without links
            {
                'paper': r'<h3 class="gs_rt">(.*?)</h3>',
                'author': r'<div class="gs_a">(.*?)</div>',
                'citation': r'Cited by (\d+)'
            },
            # Pattern 3: More flexible pattern for different layouts
            {
                'paper': r'<h3[^>]*>(.*?)</h3>',
                'author': r'<div[^>]*class="gs_a"[^>]*>(.*?)</div>',
                'citation': r'Cited by (\d+)'
            },
            # Pattern 4: Look for any h3 tags that might contain titles
            {
                'paper': r'<h3[^>]*>.*?<a[^>]*>(.*?)</a>.*?</h3>',
                'author': r'<div[^>]*class="gs_a"[^>]*>(.*?)</div>',
                'citation': r'Cited by (\d+)'
            },
            # Pattern 5: Very flexible - any h3 with text
            {
                'paper': r'<h3[^>]*>(.*?)</h3>',
                'author': r'<div[^>]*>(.*?)</div>',
                'citation': r'Cited by (\d+)'
            },
            # Pattern 6: Look for gs_rt class in different contexts
            {
                'paper': r'<div[^>]*class="gs_rt"[^>]*>.*?<a[^>]*>(.*?)</a>.*?</div>',
                'author': r'<div[^>]*class="gs_a"[^>]*>(.*?)</div>',
                'citation': r'Cited by (\d+)'
            },
            # Pattern 7: Look for any div with gs_rt class
            {
                'paper': r'<div[^>]*class="gs_rt"[^>]*>(.*?)</div>',
                'author': r'<div[^>]*class="gs_a"[^>]*>(.*?)</div>',
                'citation': r'Cited by (\d+)'
            }
        ]
        
        # Try each pattern until we find results
        for pattern_idx, pattern in enumerate(patterns):
            print(f"  Trying pattern {pattern_idx + 1}...")
            
            # Find all paper entries
            paper_matches = re.findall(pattern['paper'], html_content, re.DOTALL | re.IGNORECASE)
            author_matches = re.findall(pattern['author'], html_content, re.DOTALL | re.IGNORECASE)
            citation_matches = re.findall(pattern['citation'], html_content, re.IGNORECASE)
            
            print(f"    Paper matches: {len(paper_matches)}")
            print(f"    Author matches: {len(author_matches)}")
            print(f"    Citation matches: {len(citation_matches)}")
            
            if paper_matches:
                # Combine results
                for i in range(min(len(paper_matches), max_results)):
                    paper_info = {
                        'title': self._clean_text(paper_matches[i]) if i < len(paper_matches) else '',
                        'authors': self._clean_text(author_matches[i]) if i < len(author_matches) else '',
                        'citations': int(citation_matches[i]) if i < len(citation_matches) else 0,
                        'query': query,
                        'rank': i + 1,
                        'pattern_used': pattern_idx + 1
                    }
                    
                    # Only add papers with meaningful titles
                    if paper_info['title'] and len(paper_info['title']) > 10:
                        papers.append(paper_info)
                
                if papers:
                    print(f"    Successfully parsed {len(papers)} papers with pattern {pattern_idx + 1}")
                    break
            else:
                print(f"    Pattern {pattern_idx + 1} found no papers")
        
        # If no patterns worked, try a more aggressive approach
        if not papers:
            print("  No patterns worked, trying aggressive parsing...")
            papers = self._aggressive_parsing(html_content, query, max_results)
        
        return papers
    
    def _aggressive_parsing(self, html_content: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """More aggressive parsing approach when standard patterns fail."""
        papers = []
        
        # Look for any text that might be a paper title
        # This is a fallback method
        lines = html_content.split('\n')
        title_candidates = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 20 and len(line) < 200:  # Reasonable title length
                # Check if line contains common academic words
                academic_words = ['climate', 'change', 'mitigation', 'policy', 'analysis', 'study', 'review', 
                                'development', 'technology', 'finance', 'governance', 'social', 'economic',
                                'environmental', 'indigenous', 'political', 'international', 'cooperation',
                                'security', 'conflict', 'peace', 'labor', 'transition', 'justice']
                if any(word.lower() in line.lower() for word in academic_words):
                    title_candidates.append(line)
        
        # Take first few candidates as papers
        for i, title in enumerate(title_candidates[:max_results]):
            paper_info = {
                'title': self._clean_text(title),
                'authors': 'Unknown',
                'citations': 0,
                'query': query,
                'rank': i + 1,
                'pattern_used': 'aggressive'
            }
            papers.append(paper_info)
        
        print(f"  Aggressive parsing found {len(papers)} papers")
        return papers
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML tags and normalize text."""
        if not text:
            return ''
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        # Remove HTML entities
        clean_text = re.sub(r'&[a-zA-Z]+;', ' ', clean_text)
        clean_text = re.sub(r'&#\d+;', ' ', clean_text)
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
    def search_topic_with_subtopics(self, topic_data: Dict[str, Any], max_papers_per_query: int = 10) -> Dict[str, Any]:
        """
        Search for papers for a complete topic including main theme and subtopics.
        """
        topic_results = {
            'topic_id': topic_data['id'],
            'main_theme': topic_data['main_theme'],
            'subtopics': topic_data['subtopics'],
            'search_queries': topic_data['search_queries'],
            'papers': [],
            'total_papers_found': 0
        }
        
        all_papers = []
        
        # Search for each query
        for query in topic_data['search_queries']:
            papers = self.search_papers(query, max_papers_per_query)
            all_papers.extend(papers)
        
        # Remove duplicates based on title (basic deduplication)
        unique_papers = self._deduplicate_papers(all_papers)
        
        # Sort by citation count (descending)
        unique_papers.sort(key=lambda x: x.get('citations', 0), reverse=True)
        
        topic_results['papers'] = unique_papers
        topic_results['total_papers_found'] = len(unique_papers)
        
        return topic_results
    
    def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate papers based on title similarity."""
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            title = paper.get('title', '').lower().strip()
            # Simple similarity check (can be improved)
            if title and len(title) > 10:  # Only consider meaningful titles
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_papers.append(paper)
        
        return unique_papers
    
    def save_search_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save search results to JSON file."""
        output_data = {
            'search_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_topics_searched': len(results),
            'total_papers_found': sum(r['total_papers_found'] for r in results),
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Search results saved to {output_file}")
        return output_data

if __name__ == "__main__":
    # Test the searcher
    searcher = GoogleScholarSearcher()
    
    # Test with a sample query
    test_query = "Development as enabler of mitigation"
    results = searcher.search_papers(test_query, max_results=5)
    
    print(f"\nTest search results for: {test_query}")
    if results:
        for paper in results:
            print(f"- {paper['title']} (Citations: {paper['citations']})")
    else:
        print("No papers found. This might indicate an issue with the parsing.")
