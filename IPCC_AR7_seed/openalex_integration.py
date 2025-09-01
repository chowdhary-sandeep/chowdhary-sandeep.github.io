#!/usr/bin/env python3
"""
OpenAlex Integration Module for IPCC AR7 Seed Papers
This module integrates with OpenAlex API to find OpenAlex IDs for papers.
"""

import time
import json
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

class OpenAlexIntegration:
    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'IPCC-AR7-Seed-Papers/1.0; mailto:chowdhary@iiasa.ac.at',
            'Accept': 'application/json'
        })
        self.delay = 1  # Delay between requests to be respectful
    
    def search_paper_by_title(self, title: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for a paper by title in OpenAlex.
        Returns list of matching papers with OpenAlex IDs.
        """
        try:
            # Clean and encode title for search
            clean_title = self._clean_title_for_search(title)
            encoded_title = quote_plus(clean_title)
            
            # Search URL - use the works endpoint like in the reference script
            search_url = f"{self.base_url}/works"
            params = {
                'search': clean_title,
                'per_page': max_results,
                'mailto': 'chowdhary@iiasa.ac.at'
            }
            
            print(f"Searching OpenAlex for: {clean_title}")
            
            # Add delay to be respectful to the API
            time.sleep(self.delay)
            
            response = self.session.get(search_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                works = data.get('results', [])
                
                # Process and return results
                processed_works = []
                for work in works:
                    processed_work = self._process_work(work)
                    processed_works.append(processed_work)
                
                print(f"Found {len(processed_works)} matches in OpenAlex")
                return processed_works
            else:
                print(f"OpenAlex API error {response.status_code}: {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"Error searching OpenAlex for '{title}': {str(e)}")
            return []
    
    def _clean_title_for_search(self, title: str) -> str:
        """Clean title for better search results."""
        # Remove common punctuation and normalize
        clean_title = title.replace('"', '').replace("'", '')
        # Remove extra whitespace
        clean_title = ' '.join(clean_title.split())
        return clean_title
    
    def _process_work(self, work: Dict[str, Any]) -> Dict[str, Any]:
        """Process a work from OpenAlex API response."""
        processed = {
            'openalex_id': work.get('id', ''),
            'title': work.get('title', ''),
            'authors': [],
            'publication_year': work.get('publication_year'),
            'journal': '',
            'doi': work.get('doi', ''),
            'citations_count': work.get('cited_by_count', 0),
            'abstract': work.get('abstract_inverted_index', {}),
            'concepts': [],
            'type': work.get('type', ''),
            'open_access': False
        }
        
        # Extract journal information safely
        if work.get('primary_location') and work['primary_location'].get('source'):
            processed['journal'] = work['primary_location']['source'].get('display_name', '')
        
        # Extract open access information safely
        if work.get('open_access'):
            processed['open_access'] = work['open_access'].get('is_oa', False)
        
        # Extract authors safely
        if work.get('authorships'):
            for authorship in work['authorships']:
                if authorship.get('author'):
                    author_info = {
                        'name': authorship['author'].get('display_name', ''),
                        'openalex_id': authorship['author'].get('id', '')
                    }
                    processed['authors'].append(author_info)
        
        # Extract concepts safely
        if work.get('concepts'):
            for concept in work['concepts']:
                concept_info = {
                    'name': concept.get('display_name', ''),
                    'openalex_id': concept.get('id', ''),
                    'level': concept.get('level', 0),
                    'score': concept.get('score', 0)
                }
                processed['concepts'].append(concept_info)
        
        return processed
    
    def find_openalex_ids_for_papers(self, papers: List[Dict[str, Any]], 
                                    max_matches_per_paper: int = 3) -> List[Dict[str, Any]]:
        """
        Find OpenAlex IDs for a list of papers.
        Returns papers with OpenAlex information added.
        """
        enhanced_papers = []
        
        for paper in papers:
            print(f"\nProcessing: {paper.get('title', 'Unknown')}")
            
            # Search OpenAlex for this paper
            openalex_matches = self.search_paper_by_title(
                paper.get('title', ''), 
                max_matches_per_paper
            )
            
            # Create enhanced paper with OpenAlex info
            enhanced_paper = paper.copy()
            enhanced_paper['openalex_matches'] = openalex_matches
            
            # Find best match based on title similarity and citation count
            if openalex_matches:
                best_match = self._find_best_match(paper, openalex_matches)
                enhanced_paper['best_openalex_match'] = best_match
                enhanced_paper['openalex_id'] = best_match.get('openalex_id', '') if best_match else ''
            else:
                enhanced_paper['best_openalex_match'] = None
                enhanced_paper['openalex_id'] = ''
            
            enhanced_papers.append(enhanced_paper)
        
        return enhanced_papers
    
    def _find_best_match(self, paper: Dict[str, Any], 
                         openalex_matches: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the best matching OpenAlex paper based on title similarity and citations."""
        if not openalex_matches:
            return None
        
        # Simple scoring based on title similarity and citation count
        best_match = None
        best_score = 0
        
        paper_title = paper.get('title', '').lower()
        paper_citations = paper.get('citations', 0)
        
        for match in openalex_matches:
            match_title = match.get('title', '').lower()
            match_citations = match.get('citations_count', 0)
            
            # Calculate similarity score
            title_similarity = self._calculate_title_similarity(paper_title, match_title)
            citation_similarity = self._calculate_citation_similarity(paper_citations, match_citations)
            
            # Combined score (title similarity weighted more heavily)
            score = title_similarity * 0.7 + citation_similarity * 0.3
            
            if score > best_score:
                best_score = score
                best_match = match
        
        return best_match
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        if not title1 or not title2:
            return 0.0
        
        # Simple word overlap similarity
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_citation_similarity(self, citations1: int, citations2: int) -> float:
        """Calculate similarity between citation counts."""
        if citations1 == 0 and citations2 == 0:
            return 1.0
        if citations1 == 0 or citations2 == 0:
            return 0.0
        
        # Use logarithmic similarity to handle large differences
        log1 = max(1, citations1)
        log2 = max(1, citations2)
        
        similarity = 1 - abs(log1 - log2) / max(log1, log2)
        return max(0.0, similarity)
    
    def save_enhanced_papers(self, enhanced_papers: List[Dict[str, Any]], 
                            output_file: str):
        """Save enhanced papers with OpenAlex information to JSON file."""
        output_data = {
            'enhancement_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_papers': len(enhanced_papers),
            'papers_with_openalex_ids': len([p for p in enhanced_papers if p.get('openalex_id')]),
            'enhanced_papers': enhanced_papers
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Enhanced papers saved to {output_file}")
        return output_data

if __name__ == "__main__":
    # Test the OpenAlex integration
    openalex = OpenAlexIntegration()
    
    # Test with a sample paper
    test_paper = {
        'title': 'Climate change mitigation through technological innovation',
        'citations': 150
    }
    
    matches = openalex.search_paper_by_title(test_paper['title'])
    print(f"OpenAlex matches for test paper:")
    for match in matches:
        print(f"- {match['title']} (ID: {match['openalex_id']}, Citations: {match['citations_count']})")
