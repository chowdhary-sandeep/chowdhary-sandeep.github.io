#!/usr/bin/env python3
"""
IPCC AR7 Chapter 5: Enablers and Barriers - Search Query Definitions
This module defines targeted search queries for each topic to find the most cited and relevant papers.
"""

from typing import List, Dict, Any

class IPCCSearchQueries:
    def __init__(self):
        self.topics = self._define_topics()
    
    def _define_topics(self) -> List[Dict[str, Any]]:
        """Define search queries for each IPCC AR7 Chapter 5 topic."""
        return [
            {
                'id': 1,
                'main_theme': 'Feasibility of mitigation in different contexts and under multiple barriers and enablers',
                'search_queries': [
                    'climate change mitigation feasibility barriers enablers',
                    'climate mitigation feasibility different contexts',
                    'climate change mitigation barriers enablers analysis',
                    'mitigation feasibility assessment climate change',
                    'climate change mitigation potential feasibility'
                ],
                'key_concepts': ['feasibility', 'barriers', 'enablers', 'contexts', 'mitigation potential']
            },
            {
                'id': 2,
                'main_theme': 'Development as enabler of mitigation',
                'search_queries': [
                    'development enabler climate change mitigation',
                    'economic development climate mitigation',
                    'sustainable development climate change mitigation',
                    'development pathways climate mitigation',
                    'IPAT equation climate change'
                ],
                'key_concepts': ['development', 'economic growth', 'sustainable development', 'IPAT', 'mitigation enablers']
            },
            {
                'id': 3,
                'main_theme': 'Capacity for mitigation, including technological, institutional, economic, and human capacity',
                'search_queries': [
                    'climate change mitigation capacity technological institutional economic human',
                    'mitigation capacity building climate change',
                    'institutional capacity climate mitigation',
                    'human capacity climate change mitigation',
                    'adaptive management climate change capacity'
                ],
                'key_concepts': ['capacity building', 'institutional capacity', 'human capacity', 'adaptive management', 'mitigation capacity']
            },
            {
                'id': 4,
                'main_theme': 'Technology, including access, cost, infrastructure, innovation, scalability, replicability and speed of and disparity in adoption',
                'search_queries': [
                    'climate change mitigation technology innovation adoption',
                    'renewable energy technology diffusion adoption',
                    'technology transfer climate change mitigation',
                    'clean technology adoption barriers',
                    'technology diffusion innovation climate mitigation'
                ],
                'key_concepts': ['technology adoption', 'innovation diffusion', 'technology transfer', 'renewable energy', 'clean technology']
            },
            {
                'id': 5,
                'main_theme': 'Finance, investment, policies and governance',
                'search_queries': [
                    'climate change mitigation finance investment',
                    'climate finance governance policies',
                    'climate investment barriers enablers',
                    'climate policy governance effectiveness',
                    'climate finance mechanisms'
                ],
                'key_concepts': ['climate finance', 'investment', 'governance', 'policy effectiveness', 'financial mechanisms']
            },
            {
                'id': 6,
                'main_theme': 'Distribution of benefits, costs, and impacts of mitigation',
                'search_queries': [
                    'climate change mitigation distribution benefits costs',
                    'mitigation policy distributional effects',
                    'climate mitigation equity justice',
                    'distributional impacts climate policies',
                    'climate justice mitigation policies'
                ],
                'key_concepts': ['distributional effects', 'equity', 'justice', 'benefits', 'costs', 'impacts']
            },
            {
                'id': 7,
                'main_theme': 'Inequality and inequity within and across countries, including intergenerational aspects',
                'search_queries': [
                    'climate change inequality inequity countries',
                    'intergenerational equity climate change',
                    'climate justice international inequality',
                    'climate change social inequality',
                    'intergenerational climate justice'
                ],
                'key_concepts': ['inequality', 'inequity', 'intergenerational equity', 'climate justice', 'social inequality']
            },
            {
                'id': 8,
                'main_theme': 'Social enablers, barriers, and impacts of mitigation, including public perception and support, lifestyles and behavior, production and consumption, communication, information, engagement, education, health and well-being',
                'search_queries': [
                    'climate change mitigation social barriers enablers',
                    'public perception climate change mitigation',
                    'behavioral change climate mitigation',
                    'lifestyle changes climate change',
                    'climate communication engagement education'
                ],
                'key_concepts': ['social barriers', 'public perception', 'behavioral change', 'lifestyle', 'communication', 'engagement']
            },
            {
                'id': 9,
                'main_theme': 'Labor as enabler and barrier to mitigation, including supply, organization, wellbeing, skills',
                'search_queries': [
                    'climate change mitigation labor employment',
                    'just transition labor climate change',
                    'green jobs climate mitigation',
                    'labor market climate change transition',
                    'workforce skills climate mitigation'
                ],
                'key_concepts': ['labor', 'employment', 'just transition', 'green jobs', 'workforce skills']
            },
            {
                'id': 10,
                'main_theme': 'Just transitions',
                'search_queries': [
                    'just transition climate change',
                    'climate justice transition',
                    'equitable climate transition',
                    'social justice climate transition',
                    'just transition framework'
                ],
                'key_concepts': ['just transition', 'climate justice', 'equitable transition', 'social justice']
            },
            {
                'id': 11,
                'main_theme': 'Environmental and natural resources enablers and barriers for mitigation at national, international, and subnational levels, including land, water, natural resources, minerals, and climate services',
                'search_queries': [
                    'natural resources climate change mitigation',
                    'land use climate mitigation',
                    'water resources climate change',
                    'mineral resources climate mitigation',
                    'climate services natural resources'
                ],
                'key_concepts': ['natural resources', 'land use', 'water resources', 'minerals', 'climate services']
            },
            {
                'id': 12,
                'main_theme': 'Indigenous rights, governance, and knowledge systems',
                'search_queries': [
                    'indigenous knowledge climate change mitigation',
                    'indigenous rights climate change',
                    'traditional ecological knowledge climate',
                    'indigenous governance climate change',
                    'indigenous knowledge systems climate'
                ],
                'key_concepts': ['indigenous knowledge', 'indigenous rights', 'traditional ecological knowledge', 'indigenous governance']
            },
            {
                'id': 13,
                'main_theme': 'Political economy of mitigation including public preferences, interest groups, and political institutions',
                'search_queries': [
                    'political economy climate change mitigation',
                    'interest groups climate policy',
                    'political institutions climate change',
                    'public preferences climate policy',
                    'climate policy political economy'
                ],
                'key_concepts': ['political economy', 'interest groups', 'political institutions', 'public preferences', 'policy making']
            },
            {
                'id': 14,
                'main_theme': 'International cooperation and supply chains',
                'search_queries': [
                    'international cooperation climate change',
                    'climate change supply chains',
                    'global climate governance',
                    'international climate agreements',
                    'climate cooperation multilateral'
                ],
                'key_concepts': ['international cooperation', 'supply chains', 'global governance', 'multilateral agreements']
            },
            {
                'id': 15,
                'main_theme': 'Peace, security, and conflict, including resource competition',
                'search_queries': [
                    'climate change security conflict',
                    'climate change peace security',
                    'resource competition climate change',
                    'climate change human security',
                    'climate security conflict resolution'
                ],
                'key_concepts': ['security', 'conflict', 'peace', 'resource competition', 'human security']
            }
        ]
    
    def get_all_queries(self) -> List[str]:
        """Get all search queries from all topics."""
        all_queries = []
        for topic in self.topics:
            all_queries.extend(topic['search_queries'])
        return all_queries
    
    def get_topic_queries(self, topic_id: int) -> List[str]:
        """Get search queries for a specific topic."""
        for topic in self.topics:
            if topic['id'] == topic_id:
                return topic['search_queries']
        return []
    
    def get_topic_by_id(self, topic_id: int) -> Dict[str, Any]:
        """Get complete topic information by ID."""
        for topic in self.topics:
            if topic['id'] == topic_id:
                return topic
        return {}
    
    def print_topic_summary(self):
        """Print a summary of all topics and their search queries."""
        print("IPCC AR7 Chapter 5: Enablers and Barriers - Search Topics")
        print("=" * 80)
        print(f"Total topics: {len(self.topics)}")
        print()
        
        for topic in self.topics:
            print(f"{topic['id']:2d}. {topic['main_theme']}")
            print(f"    Key concepts: {', '.join(topic['key_concepts'])}")
            print(f"    Search queries: {len(topic['search_queries'])}")
            print()
    
    def save_topics_to_json(self, output_file: str = "search_topics.json"):
        """Save all topics and queries to a JSON file."""
        import json
        
        output_data = {
            'chapter': 'IPCC AR7 Chapter 5: Enablers and Barriers',
            'total_topics': len(self.topics),
            'total_queries': len(self.get_all_queries()),
            'topics': self.topics
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Search topics saved to {output_file}")
        return output_data

if __name__ == "__main__":
    # Test the search queries
    queries = IPCCSearchQueries()
    
    # Print summary
    queries.print_topic_summary()
    
    # Save to JSON
    queries.save_topics_to_json()
    
    # Test getting queries for a specific topic
    topic_3_queries = queries.get_topic_queries(3)
    print(f"\nSample queries for Topic 3 (Capacity for mitigation):")
    for i, query in enumerate(topic_3_queries, 1):
        print(f"  {i}. {query}")
