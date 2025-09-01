# IPCC AR7 Chapter 5: Enablers and Barriers - Seed Paper Search System

## Overview

This system automatically identifies the most cited and relevant academic papers for each topic in IPCC AR7 Chapter 5: "Enablers and Barriers." The goal is to create a comprehensive seed set of papers that can be used for systematic literature synthesis and citation network expansion.

## Purpose

As outlined in the project description, this addresses the synthesis bottleneck by:
1. **Identifying seed papers** for each IPCC topic
2. **Providing OpenAlex IDs** for systematic literature expansion
3. **Enabling citation network crawling** in both directions (backward to foundational works and forward to newer studies)
4. **Supporting semantic searches** to capture semantically linked literature

## System Architecture

The system consists of four main modules:

### 1. `topic_search_queries.py`
- Defines 15 IPCC topics with targeted search queries
- Each topic has 5-6 specific search queries combining main themes and subtopics
- Generates context-aware queries like "climate change mitigation technology innovation adoption"

### 2. `google_scholar_searcher.py`
- Searches Google Scholar for each query
- Extracts paper metadata (title, authors, citations)
- Implements rate limiting and error handling
- Returns papers sorted by citation count

### 3. `openalex_integration.py`
- Integrates with OpenAlex API to find OpenAlex IDs
- Matches papers based on title similarity and citation counts
- Provides additional metadata (DOI, journal, concepts, authors)
- Enables systematic literature expansion

### 4. `main_orchestrator.py`
- Coordinates the entire search process
- Manages topic-by-topic processing
- Handles data deduplication and enhancement
- Generates comprehensive reports and saves results

## IPCC Topics Covered

1. **Feasibility of mitigation** in different contexts and under multiple barriers and enablers
2. **Development as enabler** of mitigation
3. **Capacity for mitigation**, including technological, institutional, economic, and human capacity
4. **Technology**, including access, cost, infrastructure, innovation, scalability, replicability and speed of and disparity in adoption
5. **Finance, investment, policies and governance**
6. **Distribution of benefits, costs, and impacts** of mitigation
7. **Inequality and inequity** within and across countries, including intergenerational aspects
8. **Social enablers, barriers, and impacts** of mitigation, including public perception, lifestyles, behavior, communication, education, health
9. **Labor as enabler and barrier** to mitigation, including supply, organization, wellbeing, skills
10. **Just transitions**
11. **Environmental and natural resources** enablers and barriers for mitigation
12. **Indigenous rights, governance, and knowledge systems**
13. **Political economy of mitigation** including public preferences, interest groups, and political institutions
14. **International cooperation and supply chains**
15. **Peace, security, and conflict**, including resource competition

## Installation and Setup

### Prerequisites
- Python 3.7+
- Internet connection for Google Scholar and OpenAlex API access

### Installation
```bash
# Navigate to the IPCC_AR7_seed directory
cd IPCC_AR7_seed

# Install required packages
pip install -r requirements.txt
```

## Usage

### 1. Test the System
Before running the full search, test all components:
```bash
python test_system.py
```

### 2. Run the Complete Search
Execute the main orchestrator to search all topics:
```bash
python main_orchestrator.py
```

### 3. Run Individual Components
Test specific modules individually:
```bash
# Test topic queries
python topic_search_queries.py

# Test OpenAlex integration
python openalex_integration.py

# Test Google Scholar searcher
python google_scholar_searcher.py
```

## Output Files

The system generates several output files in the `IPCC_AR7_seed/` directory:

### Individual Topic Results
- `topic_01_results.json` to `topic_15_results.json`
- Contains all papers found for each topic with OpenAlex integration

### Comprehensive Results
- `comprehensive_results.json` - Complete dataset with all topics and papers
- `search_topics.json` - Search query definitions and topic structure
- `summary_report.txt` - Human-readable summary of all findings

### Sample Output Structure
```json
{
  "topic_id": 1,
  "main_theme": "Feasibility of mitigation in different contexts...",
  "papers_found": 45,
  "papers_with_openalex_ids": 38,
  "top_papers": [
    {
      "title": "Stabilization Wedges: Solving the Climate Problem...",
      "authors": "Pacala & Socolow",
      "citations": 3102,
      "openalex_id": "W2106176530",
      "doi": "10.1126/science.1100103"
    }
  ]
}
```

## Configuration Options

### Search Parameters
- `max_papers_per_query`: Number of papers to retrieve per search query (default: 15)
- `max_openalex_matches`: Number of OpenAlex matches to consider per paper (default: 3)

### Rate Limiting
- Google Scholar: Random delays between 2-5 seconds
- OpenAlex: 1-second delay between requests (respectful API usage)

## Expected Results

Based on the GPT agent's findings, the system should identify papers like:

- **Topic 1**: Pacala & Socolow (2004) - "Stabilization Wedges" (~3,102 citations)
- **Topic 4**: Chu & Majumdar (2012) - "Opportunities and challenges for sustainable energy" (~10,774 citations)
- **Topic 5**: Stern (2007) - "Economics of Climate Change" (~10,169 citations)
- **Topic 11**: Rockström et al. (2009) - "Safe operating space for humanity" (~11,838 citations)

## Error Handling

The system includes comprehensive error handling for:
- Network timeouts and connection issues
- API rate limiting
- Malformed search results
- Missing paper metadata
- OpenAlex API failures

## Future Enhancements

Potential improvements for the system:
1. **Semantic search integration** using embeddings
2. **Citation network analysis** to identify foundational papers
3. **Journal impact factor weighting** in paper ranking
4. **Multi-language support** for international literature
5. **Automated quality assessment** of paper relevance

## Contributing

To contribute to this system:
1. Test the current implementation
2. Identify areas for improvement
3. Implement enhancements following the modular architecture
4. Update documentation and tests

## License

This system is developed for academic research purposes related to IPCC AR7 synthesis.

## Contact

For questions or issues related to this system, please refer to the project documentation or contact the development team.

---

**Note**: This system is designed to be respectful of academic search services and APIs. It includes appropriate delays and error handling to avoid overwhelming external services.
