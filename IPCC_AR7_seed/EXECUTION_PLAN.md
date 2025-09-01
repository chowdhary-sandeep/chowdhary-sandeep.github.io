# IPCC AR7 Chapter 5 Seed Papers - Execution Plan

## System Overview

This system has been built to automatically identify the most cited and relevant academic papers for each of the 15 topics in IPCC AR7 Chapter 5: "Enablers and Barriers." The system follows the approach outlined in your project description to create seed papers that can be used for systematic literature synthesis.

## What the System Does

1. **Defines 15 targeted topics** based on the IPCC AR7 Chapter 5 outline
2. **Generates context-aware search queries** for each topic (e.g., "climate change mitigation technology innovation adoption")
3. **Searches Google Scholar** for each query to get citation counts and paper metadata
4. **Integrates with OpenAlex API** to find OpenAlex IDs for systematic literature expansion
5. **Saves comprehensive results** including top papers per topic with OpenAlex IDs

## System Architecture

```
IPCC_AR7_seed/
├── topic_search_queries.py      # Defines 15 topics with search queries
├── google_scholar_searcher.py   # Searches Google Scholar for papers
├── openalex_integration.py      # Finds OpenAlex IDs for papers
├── main_orchestrator.py         # Coordinates the entire process
├── test_system.py               # Tests all components
├── requirements.txt              # Python dependencies
├── README.md                    # Comprehensive documentation
├── run_search.bat               # Windows batch file for easy execution
└── EXECUTION_PLAN.md            # This file
```

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

## Expected Results

Based on the GPT agent's findings, the system should identify papers like:

- **Topic 1**: Pacala & Socolow (2004) - "Stabilization Wedges" (~3,102 citations)
- **Topic 4**: Chu & Majumdar (2012) - "Opportunities and challenges for sustainable energy" (~10,774 citations)  
- **Topic 5**: Stern (2007) - "Economics of Climate Change" (~10,169 citations)
- **Topic 11**: Rockström et al. (2009) - "Safe operating space for humanity" (~11,838 citations)

## Step-by-Step Execution

### Step 1: Test the System
```bash
cd IPCC_AR7_seed
python test_system.py
```
This verifies all components work correctly.

### Step 2: Run the Complete Search
```bash
python main_orchestrator.py
```
This will:
- Search all 15 topics systematically
- Find papers for each topic using Google Scholar
- Enhance papers with OpenAlex IDs
- Save results to individual topic files
- Generate comprehensive summary reports

### Step 3: Review Results
Check the generated files:
- `topic_01_results.json` to `topic_15_results.json` - Individual topic results
- `comprehensive_results.json` - Complete dataset
- `summary_report.txt` - Human-readable summary

## Output Structure

Each topic result contains:
```json
{
  "topic_id": 1,
  "main_theme": "Feasibility of mitigation...",
  "papers_found": 45,
  "papers_with_openalex_ids": 38,
  "top_papers": [
    {
      "title": "Paper Title",
      "authors": "Author Names", 
      "citations": 3102,
      "openalex_id": "W2106176530",
      "doi": "10.1126/science.1100103"
    }
  ],
  "all_papers": [...]
}
```

## Time Estimates

- **Testing**: 2-3 minutes
- **Full search**: 30-60 minutes (depending on network conditions)
- **Total papers expected**: 200-400+ papers across all topics

## Next Steps After Execution

1. **Review top papers** for each topic to ensure quality
2. **Use OpenAlex IDs** for citation network expansion
3. **Integrate with your systematic literature synthesis tool**
4. **Expand literature coverage** using the seed papers as starting points

## Integration with Your Project

This system directly supports your project's goal to:
> "build an automated, systematic literature synthesis tool for climate science that keeps IPCC reports continuously updated with minimal manual supervision"

The seed papers provide the foundation for:
- **Citation network crawling** in both directions
- **Semantic searches** to capture linked literature
- **Systematic coverage** of IPCC-relevant literature

## Troubleshooting

- **Rate limiting**: The system includes delays to avoid overwhelming services
- **Network issues**: Comprehensive error handling for timeouts and failures
- **API failures**: Graceful degradation if OpenAlex or Google Scholar are unavailable

## Success Metrics

The system is successful if it:
- ✅ Finds at least 10-20 papers per topic
- ✅ Provides OpenAlex IDs for 70%+ of papers
- ✅ Identifies highly cited papers (>100 citations) for each topic
- ✅ Covers all 15 IPCC topics comprehensively

---

**Ready to execute?** Run `python test_system.py` first, then `python main_orchestrator.py` to begin the systematic search for IPCC AR7 Chapter 5 seed papers.
