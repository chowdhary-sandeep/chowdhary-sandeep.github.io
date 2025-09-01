#!/usr/bin/env python3
"""
Test script for IPCC AR7 Seed Paper Search System
This script tests individual components before running the full search.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing module imports...")
    
    try:
        from topic_search_queries import IPCCSearchQueries
        print("✓ IPCCSearchQueries imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import IPCCSearchQueries: {e}")
        return False
    
    try:
        from google_scholar_searcher import GoogleScholarSearcher
        print("✓ GoogleScholarSearcher imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import GoogleScholarSearcher: {e}")
        return False
    
    try:
        from openalex_integration import OpenAlexIntegration
        print("✓ OpenAlexIntegration imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import OpenAlexIntegration: {e}")
        return False
    
    return True

def test_topic_queries():
    """Test the topic queries module."""
    print("\nTesting topic queries...")
    
    try:
        from topic_search_queries import IPCCSearchQueries
        
        queries = IPCCSearchQueries()
        print(f"✓ Created IPCCSearchQueries with {len(queries.topics)} topics")
        
        # Test getting queries for a specific topic
        topic_3_queries = queries.get_topic_queries(3)
        print(f"✓ Topic 3 has {len(topic_3_queries)} search queries")
        
        # Test saving to JSON
        queries.save_topics_to_json()
        print("✓ Successfully saved topics to JSON")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing topic queries: {e}")
        return False

def test_openalex_integration():
    """Test the OpenAlex integration module."""
    print("\nTesting OpenAlex integration...")
    
    try:
        from openalex_integration import OpenAlexIntegration
        
        openalex = OpenAlexIntegration()
        print("✓ Created OpenAlexIntegration instance")
        
        # Test with a simple search
        test_paper = {
            'title': 'Climate change mitigation through technological innovation',
            'citations': 150
        }
        
        matches = openalex.search_paper_by_title(test_paper['title'], max_results=2)
        print(f"✓ OpenAlex search returned {len(matches)} matches")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing OpenAlex integration: {e}")
        return False

def test_google_scholar_searcher():
    """Test the Google Scholar searcher module."""
    print("\nTesting Google Scholar searcher...")
    
    try:
        from google_scholar_searcher import GoogleScholarSearcher
        
        searcher = GoogleScholarSearcher()
        print("✓ Created GoogleScholarSearcher instance")
        
        # Note: We won't actually search to avoid rate limiting during testing
        print("✓ Google Scholar searcher initialized (search functionality not tested to avoid rate limiting)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing Google Scholar searcher: {e}")
        return False

def main():
    """Run all tests."""
    print("IPCC AR7 Seed Paper Search System - Component Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_topic_queries,
        test_openalex_integration,
        test_google_scholar_searcher
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The system is ready to use.")
        print("\nTo run the full search, execute:")
        print("  python main_orchestrator.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
