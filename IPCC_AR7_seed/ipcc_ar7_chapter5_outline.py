#!/usr/bin/env python3
"""
IPCC AR7 Chapter 5: Enablers and Barriers - Topic Parser
This script parses the chapter outline and structures topics for systematic literature search.
"""

import json
import re
from typing import List, Dict, Any

class IPCCOutlineParser:
    def __init__(self):
        self.chapter_outline = """
        • Feasibility of mitigation in different contexts and under multiple barriers and enablers
        • Development as enabler of mitigation
        • Capacity for mitigation, including technological, institutional, economic, and human capacity
        • Technology, including access, cost, infrastructure, innovation, scalability, replicability and speed of and disparity in adoption
        • Finance, investment, policies and governance
        • Distribution of benefits, costs, and impacts of mitigation
        • Inequality and inequity within and across countries, including intergenerational aspects
        • Social enablers, barriers, and impacts of mitigation, including public perception and support, lifestyles and behavior, production and consumption, communication, information, engagement, education, health and well-being
        • Labor as enabler and barrier to mitigation, including supply, organization, wellbeing, skills
        • Just transitions
        • Environmental and natural resources enablers and barriers for mitigation at national, international, and subnational levels, including land, water, natural resources, minerals, and climate services
        • Indigenous rights, governance, and knowledge systems
        • Political economy of mitigation including public preferences, interest groups, and political institutions
        • International cooperation and supply chains
        • Peace, security, and conflict, including resource competition
        """
    
    def parse_outline(self) -> List[Dict[str, Any]]:
        """Parse the outline into structured topics with main themes and subtopics."""
        topics = []
        
        # Split by bullet points
        bullet_points = [point.strip() for point in self.chapter_outline.split('•') if point.strip()]
        
        for i, point in enumerate(bullet_points):
            # Extract main theme (before first comma)
            if ',' in point:
                main_theme = point.split(',')[0].strip()
                # Extract subtopics (after first comma)
                subtopics_text = ','.join(point.split(',')[1:]).strip()
                subtopics = [st.strip() for st in subtopics_text.split(',') if st.strip()]
            else:
                main_theme = point.strip()
                subtopics = []
            
            topic_dict = {
                'id': i + 1,
                'main_theme': main_theme,
                'subtopics': subtopics,
                'full_text': point.strip(),
                'search_queries': self._generate_search_queries(main_theme, subtopics)
            }
            topics.append(topic_dict)
        
        return topics
    
    def _generate_search_queries(self, main_theme: str, subtopics: List[str]) -> List[str]:
        """Generate search queries for each topic and subtopic."""
        queries = []
        
        # Add main theme query
        queries.append(f"climate change mitigation {main_theme}")
        
        # Add subtopic queries with context
        for subtopic in subtopics:
            # Clean up subtopic text
            clean_subtopic = re.sub(r'\s+', ' ', subtopic).strip()
            if clean_subtopic:
                queries.append(f"climate change mitigation {main_theme} {clean_subtopic}")
        
        return queries
    
    def save_parsed_outline(self, output_file: str = "parsed_outline.json"):
        """Save the parsed outline to a JSON file."""
        topics = self.parse_outline()
        
        output_data = {
            'chapter': 'IPCC AR7 Chapter 5: Enablers and Barriers',
            'total_topics': len(topics),
            'topics': topics
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Parsed outline saved to {output_file}")
        return output_data
    
    def print_summary(self):
        """Print a summary of the parsed outline."""
        topics = self.parse_outline()
        
        print("IPCC AR7 Chapter 5: Enablers and Barriers")
        print("=" * 60)
        print(f"Total main topics: {len(topics)}")
        print()
        
        for topic in topics:
            print(f"{topic['id']}. {topic['main_theme']}")
            if topic['subtopics']:
                for subtopic in topic['subtopics']:
                    print(f"   • {subtopic}")
            print(f"   Search queries: {len(topic['search_queries'])}")
            print()

if __name__ == "__main__":
    parser = IPCCOutlineParser()
    
    # Parse and save outline
    parsed_data = parser.save_parsed_outline("IPCC_AR7_seed/parsed_outline.json")
    
    # Print summary
    parser.print_summary()
