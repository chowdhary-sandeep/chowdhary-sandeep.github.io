#!/usr/bin/env python3
"""
IPCC AR7 Chapter 5 Seed Papers - Main Orchestrator
This script coordinates the entire process of finding seed papers for each IPCC topic.
"""

import time
import json
import os
import pandas as pd
from typing import List, Dict, Any
from topic_search_queries import IPCCSearchQueries
from google_scholar_searcher import GoogleScholarSearcher
from openalex_integration import OpenAlexIntegration

class IPCCSeedPaperOrchestrator:
    def __init__(self):
        self.topics = IPCCSearchQueries()
        self.scholar_searcher = GoogleScholarSearcher()
        self.openalex_integration = OpenAlexIntegration()
        self.output_dir = "IPCC_AR7_seed"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run_complete_search(self, max_papers_per_query: int = 15, 
                           max_openalex_matches: int = 10):
        """
        Run the complete search process for all IPCC topics.
        Note: Google Scholar searches are limited due to anti-bot measures,
        so we focus on OpenAlex searches which are more reliable.
        """
        print("IPCC AR7 Chapter 5: Enablers and Barriers - Seed Paper Search")
        print("=" * 80)
        print("Note: Google Scholar searches are limited due to anti-bot measures.")
        print("Focusing on OpenAlex searches for reliable results.")
        print(f"Starting search for {len(self.topics.topics)} topics...")
        print()
        
        all_results = []
        total_openalex_papers = 0
        
        # Process each topic
        for topic in self.topics.topics:
            print(f"\n{'='*60}")
            print(f"Processing Topic {topic['id']}: {topic['main_theme']}")
            print(f"{'='*60}")
            
            # Try Google Scholar search (may be limited)
            try:
                topic_results = self._search_topic_papers(topic, max_papers_per_query)
                print(f"  Google Scholar: Found {len(topic_results)} papers")
            except Exception as e:
                print(f"  Google Scholar search failed: {str(e)}")
                topic_results = []
            
            # Search OpenAlex for top papers (primary source)
            openalex_results = self._search_openalex_for_topic(topic, max_openalex_matches)
            print(f"  OpenAlex: Found {len(openalex_results)} papers")
            
            # Store results
            topic_summary = {
                'topic_id': topic['id'],
                'main_theme': topic['main_theme'],
                'key_concepts': topic['key_concepts'],
                'search_queries': topic['search_queries'],
                'google_scholar_papers': len(topic_results),
                'openalex_papers_found': len(openalex_results),
                'top_google_scholar_papers': self._get_top_papers(topic_results, top_n=5),
                'openalex_top_papers': self._get_top_openalex_papers(openalex_results, top_n=5),
                'all_google_scholar_papers': topic_results,
                'all_openalex_papers': openalex_results
            }
            
            all_results.append(topic_summary)
            total_openalex_papers += len(openalex_results)
            
            # Save individual topic results
            self._save_topic_results(topic_summary, topic['id'])
            
            print(f"Topic {topic['id']} completed: {len(topic_results)} Google Scholar papers, {len(openalex_results)} OpenAlex papers")
        
        # Save comprehensive results
        self._save_comprehensive_results(all_results, total_openalex_papers)
        
        # Generate summary report
        self._generate_summary_report(all_results)
        
        # Create joint Excel file
        self._create_joint_excel_file(all_results)
        
        print(f"\n{'='*80}")
        print("SEARCH COMPLETED SUCCESSFULLY!")
        print(f"Total topics processed: {len(all_results)}")
        print(f"Total OpenAlex papers found: {total_openalex_papers}")
        print(f"Results saved in: {self.output_dir}/")
        print(f"{'='*80}")
        
        return all_results
    
    def _search_topic_papers(self, topic: Dict[str, Any], max_papers_per_query: int) -> List[Dict[str, Any]]:
        """Search for papers for a specific topic using Google Scholar."""
        all_papers = []
        
        print(f"Searching Google Scholar with {len(topic['search_queries'])} queries...")
        
        for i, query in enumerate(topic['search_queries'], 1):
            print(f"  Query {i}/{len(topic['search_queries'])}: {query}")
            
            try:
                papers = self.scholar_searcher.search_papers(query, max_papers_per_query)
                
                # Add topic context to each paper
                for paper in papers:
                    paper['topic_id'] = topic['id']
                    paper['topic_theme'] = topic['main_theme']
                    paper['search_query'] = query
                
                all_papers.extend(papers)
                
                print(f"    Found {len(papers)} papers")
                
            except Exception as e:
                print(f"    Error searching query '{query}': {str(e)}")
                continue
        
        # Remove duplicates and sort by citations
        unique_papers = self._deduplicate_papers(all_papers)
        unique_papers.sort(key=lambda x: x.get('citations', 0), reverse=True)
        
        print(f"Total unique Google Scholar papers found: {len(unique_papers)}")
        return unique_papers
    
    def _search_openalex_for_topic(self, topic: Dict[str, Any], max_matches: int) -> List[Dict[str, Any]]:
        """Search OpenAlex separately for top papers on this topic."""
        openalex_papers = []
        
        print(f"Searching OpenAlex for top papers on: {topic['main_theme']}")
        
        # Search strategies for better coverage
        search_strategies = [
            # Strategy 1: Main theme with climate change
            f"climate change mitigation {topic['main_theme']}",
            # Strategy 2: Key concepts with climate change
            f"climate change {topic['key_concepts'][0] if topic['key_concepts'] else 'mitigation'}",
            # Strategy 3: Broader climate search
            f"climate change {topic['main_theme'].split()[0:3]}",
            # Strategy 4: Specific IPCC-related terms
            f"IPCC climate change {topic['key_concepts'][0] if topic['key_concepts'] else 'mitigation'}",
            # Strategy 5: Just the main theme
            topic['main_theme']
        ]
        
        for i, strategy in enumerate(search_strategies, 1):
            print(f"  Strategy {i}: {strategy}")
            
            try:
                strategy_papers = self.openalex_integration.search_paper_by_title(
                    strategy, max_matches // len(search_strategies)
                )
                
                # Add topic context
                for paper in strategy_papers:
                    paper['topic_id'] = topic['id']
                    paper['topic_theme'] = topic['main_theme']
                    paper['search_source'] = f'strategy_{i}_{strategy[:30]}'
                
                openalex_papers.extend(strategy_papers)
                print(f"    Found {len(strategy_papers)} papers")
                
            except Exception as e:
                print(f"    Error with strategy {i}: {str(e)}")
                continue
        
        # Remove duplicates and sort by citations
        unique_openalex = self._deduplicate_openalex_papers(openalex_papers)
        unique_openalex.sort(key=lambda x: x.get('citations_count', 0), reverse=True)
        
        print(f"Total unique OpenAlex papers found: {len(unique_openalex)}")
        return unique_openalex
    
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
    
    def _deduplicate_openalex_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate OpenAlex papers based on title similarity."""
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            title = paper.get('title', '').lower().strip()
            if title and len(title) > 10:
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_papers.append(paper)
        
        return unique_papers
    
    def _get_top_papers(self, papers: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top N Google Scholar papers by citation count."""
        sorted_papers = sorted(papers, key=lambda x: x.get('citations', 0), reverse=True)
        return sorted_papers[:top_n]
    
    def _get_top_openalex_papers(self, papers: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top N OpenAlex papers by citation count."""
        sorted_papers = sorted(papers, key=lambda x: x.get('citations_count', 0), reverse=True)
        return sorted_papers[:top_n]
    
    def _save_topic_results(self, topic_results: Dict[str, Any], topic_id: int):
        """Save results for a specific topic."""
        filename = f"topic_{topic_id:02d}_results.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(topic_results, f, indent=2, ensure_ascii=False)
        
        print(f"Topic {topic_id} results saved to: {filename}")
    
    def _save_comprehensive_results(self, all_results: List[Dict[str, Any]], total_papers: int):
        """Save comprehensive results for all topics."""
        comprehensive_data = {
            'search_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'chapter': 'IPCC AR7 Chapter 5: Enablers and Barriers',
            'total_topics': len(all_results),
            'total_google_scholar_papers': sum(r['google_scholar_papers'] for r in all_results),
            'total_openalex_papers': total_papers,
            'topics_summary': [
                {
                    'topic_id': r['topic_id'],
                    'main_theme': r['main_theme'],
                    'google_scholar_papers': r['google_scholar_papers'],
                    'openalex_papers': r['openalex_papers_found'],
                    'top_google_scholar_papers': r['top_google_scholar_papers'],
                    'top_openalex_papers': r['openalex_top_papers']
                }
                for r in all_results
            ],
            'all_results': all_results
        }
        
        filepath = os.path.join(self.output_dir, "comprehensive_results.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        print(f"Comprehensive results saved to: comprehensive_results.json")
    
    def _create_joint_excel_file(self, all_results: List[Dict[str, Any]]):
        """Create a joint Excel file combining all results."""
        print("Creating joint Excel file...")
        
        # Prepare data for Excel
        excel_data = []
        
        for topic_result in all_results:
            topic_id = topic_result['topic_id']
            main_theme = topic_result['main_theme']
            
            # Add Google Scholar papers
            for paper in topic_result['all_google_scholar_papers']:
                excel_data.append({
                    'Topic_ID': topic_id,
                    'Main_Theme': main_theme,
                    'Source': 'Google Scholar',
                    'Title': paper.get('title', ''),
                    'Authors': paper.get('authors', ''),
                    'Citations': paper.get('citations', 0),
                    'Journal': '',
                    'DOI': '',
                    'OpenAlex_ID': '',
                    'Publication_Year': '',
                    'Search_Query': paper.get('search_query', ''),
                    'Pattern_Used': paper.get('pattern_used', ''),
                    'Rank': paper.get('rank', 0)
                })
            
            # Add OpenAlex papers
            for paper in topic_result['all_openalex_papers']:
                excel_data.append({
                    'Topic_ID': topic_id,
                    'Main_Theme': main_theme,
                    'Source': 'OpenAlex',
                    'Title': paper.get('title', ''),
                    'Authors': ', '.join([author.get('name', '') for author in paper.get('authors', [])]),
                    'Citations': paper.get('citations_count', 0),
                    'Journal': paper.get('journal', ''),
                    'DOI': paper.get('doi', ''),
                    'OpenAlex_ID': paper.get('openalex_id', ''),
                    'Publication_Year': paper.get('publication_year', ''),
                    'Search_Query': paper.get('search_source', ''),
                    'Pattern_Used': 'OpenAlex API',
                    'Rank': 0
                })
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(excel_data)
        
        # Sort by topic ID, source, and citations
        df = df.sort_values(['Topic_ID', 'Source', 'Citations'], ascending=[True, True, False])
        
        excel_path = os.path.join(self.output_dir, "IPCC_AR7_Chapter5_All_Papers.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='All_Papers', index=False)
            
            # Summary sheet
            summary_data = []
            for topic_result in all_results:
                summary_data.append({
                    'Topic_ID': topic_result['topic_id'],
                    'Main_Theme': topic_result['main_theme'],
                    'Google_Scholar_Papers': topic_result['google_scholar_papers'],
                    'OpenAlex_Papers': topic_result['openalex_papers_found'],
                    'Total_Papers': topic_result['google_scholar_papers'] + topic_result['openalex_papers_found']
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Top papers sheet
            top_papers_data = []
            for topic_result in all_results:
                topic_id = topic_result['topic_id']
                main_theme = topic_result['main_theme']
                
                # Top Google Scholar papers
                for i, paper in enumerate(topic_result['top_google_scholar_papers'][:3], 1):
                    top_papers_data.append({
                        'Topic_ID': topic_id,
                        'Main_Theme': main_theme,
                        'Source': 'Google Scholar',
                        'Rank': i,
                        'Title': paper.get('title', ''),
                        'Citations': paper.get('citations', 0),
                        'Authors': paper.get('authors', '')
                    })
                
                # Top OpenAlex papers
                for i, paper in enumerate(topic_result['openalex_top_papers'][:3], 1):
                    top_papers_data.append({
                        'Topic_ID': topic_id,
                        'Main_Theme': main_theme,
                        'Source': 'OpenAlex',
                        'Rank': i,
                        'Title': paper.get('title', ''),
                        'Citations': paper.get('citations_count', 0),
                        'Authors': ', '.join([author.get('name', '') for author in paper.get('authors', [])])
                    })
            
            top_papers_df = pd.DataFrame(top_papers_data)
            top_papers_df.to_excel(writer, sheet_name='Top_Papers', index=False)
        
        print(f"Joint Excel file created: IPCC_AR7_Chapter5_All_Papers.xlsx")
        print(f"Contains {len(df)} total papers across all topics")
    
    def _generate_summary_report(self, all_results: List[Dict[str, Any]]):
        """Generate a human-readable summary report."""
        report_lines = [
            "IPCC AR7 Chapter 5: Enablers and Barriers - Seed Papers Summary Report",
            "=" * 80,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Topics: {len(all_results)}",
            "",
            "TOPIC SUMMARIES:",
            ""
        ]
        
        for result in all_results:
            report_lines.extend([
                f"Topic {result['topic_id']}: {result['main_theme']}",
                f"  Google Scholar papers: {result['google_scholar_papers']}",
                f"  OpenAlex papers: {result['openalex_papers_found']}",
                "  Top Google Scholar papers by citations:"
            ])
            
            for i, paper in enumerate(result['top_google_scholar_papers'][:3], 1):
                title = paper.get('title', 'Unknown')[:80]
                citations = paper.get('citations', 0)
                report_lines.append(f"    {i}. {title} (Citations: {citations})")
            
            report_lines.append("  Top OpenAlex papers by citations:")
            for i, paper in enumerate(result['openalex_top_papers'][:3], 1):
                title = paper.get('title', 'Unknown')[:80]
                citations = paper.get('citations_count', 0)
                openalex_id = paper.get('openalex_id', 'N/A')
                report_lines.append(f"    {i}. {title} (Citations: {citations}, OpenAlex: {openalex_id})")
            
            report_lines.append("")
        
        # Save report
        report_path = os.path.join(self.output_dir, "summary_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"Summary report saved to: summary_report.txt")

def main():
    """Main execution function."""
    print("Starting IPCC AR7 Chapter 5 Seed Paper Search...")
    
    # Initialize orchestrator
    orchestrator = IPCCSeedPaperOrchestrator()
    
    try:
        # Run the complete search process
        results = orchestrator.run_complete_search(
            max_papers_per_query=15,  # Adjust based on needs
            max_openalex_matches=10
        )
        
        print("\nSearch completed successfully!")
        return results
        
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
        return None
    except Exception as e:
        print(f"\nError during search: {str(e)}")
        return None

if __name__ == "__main__":
    main()
