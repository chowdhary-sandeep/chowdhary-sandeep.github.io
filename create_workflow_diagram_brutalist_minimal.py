import graphviz
import os
import json

def create_brutalist_minimal_diagram():
    """Create a brutalist, minimalist workflow diagram with no visual styling"""
    dot = graphviz.Digraph(format='svg')
    
    # Match original dimensions
    dot.attr(rankdir='TB', size='12.1,12.32')
    dot.attr('graph', ranksep='0.72', nodesep='0.6')
    
    # Brutalist node attributes - plain boxes, no colors, no rounded corners
    dot.attr('node', shape='box', style='filled', fillcolor='white', 
             width='2.4', height='0.8', fontsize='19.6', fontname='monospace')
    dot.attr('edge', fontsize='19.6', fontname='monospace')
    
    # Status indicators using simple text
    done = '[DONE]'
    hard = '[HARD]'
    medium = '[MED]'
    
    # Nodes with brutalist naming and status
    dot.node('S', f'SEARCH STRATEGY {medium}\nOpenAlex metadata')
    dot.node('L', f'LITERATURE COLLECTOR {done}\nOpenAlex metadata')
    dot.node('FPC', f'FULL PAPER COLLECTOR {hard}\nif Open Access')
    dot.node('ML', f'ML CLASSIFIER {done}\nassigns to IPCC sections')
    dot.node('KIE', f'KEY INSIGHT EXTRACTOR {done}\nLLM')
    dot.node('VAL', f'VALIDATOR AI {medium}\nchecks insights')
    dot.node('IPCC', f'LIVE EDITOR AGENT {medium}\nIPCC HTML')
    dot.node('PLAC', f'PLACEMENT IN IPCC {done}')
    dot.node('KG', f'KNOWLEDGE GRAPH GEN {hard}')
    dot.node('CE', f'CONCEPTUAL ENRICHMENT {hard}\nLatent Information')
    dot.node('AT', f'AUTO-THINK LAYER {hard}\nClimate Science')
    dot.node('NS', f'NEW SCIENCE OUTPUT {hard}')
    
    # Main workflow cluster - no visual styling
    with dot.subgraph(name='cluster_0') as main:
        main.attr(label='LIVE-UPDATED IPCC REPORT', labelloc='t', 
                 fontsize='24', fontname='monospace')
        # Workflow edges
        main.edge('S', 'L', label='update')
        main.edge('L', 'S', label='feedback')
        main.edge('L', 'FPC', label='DOI + metadata')
        main.edge('FPC', 'ML', label='paper/abstract')
        main.edge('FPC', 'KIE', label='paper/abstract')
        main.edge('ML', 'PLAC')
        main.edge('KIE', 'PLAC', label='insights')
        main.edge('KIE', 'VAL', label='insights')
        main.edge('VAL', 'IPCC', label='validation')
        main.edge('VAL', 'PLAC', label='validated')
        main.edge('PLAC', 'IPCC')
    
    # AI processing cluster - no visual styling
    with dot.subgraph(name='cluster_1') as ai:
        ai.attr(label='AUTO-THINK LAYER FOR NEW SCIENCE', 
                labelloc='t', fontsize='24', fontname='monospace')
        # AI processing nodes
        ai.node('KG', 'KNOWLEDGE GRAPH GEN')
        ai.node('CE', 'CONCEPTUAL ENRICHMENT\nLatent Information')
        ai.node('AT', 'AUTO-THINK LAYER\nClimate Science')
        ai.node('NS', 'NEW SCIENCE OUTPUT')
    
    # Connect main workflow to AI processing
    dot.edge('KIE', 'KG', label='insights')
    dot.edge('KG', 'CE', label='graph')
    dot.edge('CE', 'AT', label='concepts')
    dot.edge('AT', 'NS', label='findings')
    
    return dot

def create_node_info():
    """Create node information dictionary for brutalist minimal version"""
    return {
        'S': {
            'title': 'SEARCH STRATEGY [MED]',
            'desc': 'Updates search criteria based on Literature Collector feedback',
            'data': 'Input: Collector feedback\nOutput: Search parameters\nAPI: OpenAlex\nStatus: In Progress [MED]',
            'status': 'medium'
        },
        'L': {
            'title': 'LITERATURE COLLECTOR [DONE]',
            'desc': 'Collects metadata from OpenAlex API: DOI, OA status, title, abstract, year',
            'data': 'Input: Search parameters\nOutput: Paper metadata\nAPI: OpenAlex\nStatus: Completed [DONE]',
            'status': 'done'
        },
        'FPC': {
            'title': 'FULL PAPER COLLECTOR [HARD]',
            'desc': 'Retrieves full paper content for Open Access papers, abstract otherwise',
            'data': 'Input: DOI + metadata\nOutput: Full paper or abstract\nStatus: Not Started [HARD]',
            'status': 'hard'
        },
        'ML': {
            'title': 'ML CLASSIFIER [DONE]',
            'desc': 'Zeroshot ML classifier assigns papers to IPCC sections',
            'data': 'Input: Paper content\nOutput: IPCC section assignment\nStatus: Completed [DONE]',
            'status': 'done'
        },
        'KIE': {
            'title': 'KEY INSIGHT EXTRACTOR [DONE]',
            'desc': 'LLM extracts key insights from papers',
            'data': 'Input: Paper content\nOutput: Key insights\nStatus: Completed [DONE]',
            'status': 'done'
        },
        'VAL': {
            'title': 'VALIDATOR AI [MED]',
            'desc': 'AI validates extracted key insights',
            'data': 'Input: Key insights\nOutput: Validation score\nStatus: In Progress [MED]',
            'status': 'medium'
        },
        'IPCC': {
            'title': 'LIVE EDITOR AGENT [MED]',
            'desc': 'Updates IPCC HTML with validated insights',
            'data': 'Input: Validated insights\nOutput: Updated IPCC HTML\nStatus: In Progress [MED]',
            'status': 'medium'
        },
        'PLAC': {
            'title': 'PLACEMENT IN IPCC [DONE]',
            'desc': 'Places validated insights into appropriate IPCC sections',
            'data': 'Input: Validated insights\nOutput: IPCC placement\nStatus: Completed [DONE]',
            'status': 'done'
        },
        'KG': {
            'title': 'KNOWLEDGE GRAPH GEN [HARD]',
            'desc': 'AI-driven knowledge graph generation from insights',
            'data': 'Input: Key insights\nOutput: Knowledge graph\nStatus: Not Started [HARD]',
            'status': 'hard'
        },
        'CE': {
            'title': 'CONCEPTUAL ENRICHMENT [HARD]',
            'desc': 'Latent information inference and conceptual enrichment',
            'data': 'Input: Knowledge graph\nOutput: Enriched concepts\nStatus: Not Started [HARD]',
            'status': 'hard'
        },
        'AT': {
            'title': 'AUTO-THINK LAYER [HARD]',
            'desc': 'Auto-think layer for climate science discovery',
            'data': 'Input: Enriched concepts\nOutput: Novel insights\nStatus: Not Started [HARD]',
            'status': 'hard'
        },
        'NS': {
            'title': 'NEW SCIENCE OUTPUT [HARD]',
            'desc': 'Generates new scientific findings and hypotheses',
            'data': 'Input: Novel insights\nOutput: New science\nStatus: Not Started [HARD]',
            'status': 'hard'
        }
    }

def create_brutalist_html_wrapper(svg_content, node_info):
    """Create brutalist, minimalist HTML wrapper with proper layout and click events"""
    node_info_json = json.dumps(node_info)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>IPCC Workflow - Brutalist Minimal</title>
    <style>
        /* Brutalist minimal styling with proper layout */
        body {{ 
            font-family: monospace; 
            margin: 0;
            padding: 20px;
            display: flex;
            gap: 20px;
            background: white; 
            color: black; 
        }}
        #diagram {{ 
            flex: 2;
            min-width: 75%;
            border: 2px solid black;
        }}
        #info-panel {{ 
            flex: 1;
            max-width: 400px;
            padding: 20px;
            background-color: #f0f0f0;
            border: 2px solid black;
            position: sticky;
            top: 20px;
            height: fit-content;
        }}
        .info-title {{ 
            font-size: 16px; 
            font-weight: bold; 
            margin-bottom: 10px; 
            border-bottom: 1px solid black; 
            padding-bottom: 5px; 
        }}
        .info-desc {{ 
            margin-bottom: 10px; 
            font-size: 14px; 
        }}
        .info-data {{ 
            font-family: monospace; 
            font-size: 12px; 
            white-space: pre-line; 
            border: 1px solid black; 
            padding: 10px; 
            background: white; 
        }}
        /* Status indicators using simple text styling */
        .status-done {{ font-weight: bold; }}
        .status-hard {{ font-weight: bold; }}
        .status-medium {{ font-weight: bold; }}
        .io {{ font-weight: bold; }}
        /* SVG styling - brutalist with matching dimensions */
        #diagram g.cluster text {{ font-size: 24px; font-weight: bold; }}
        #diagram g.node text {{ font-size: 19.6px; }}
        #diagram g.edge text {{ font-size: 19.6px; }}
        #diagram g.node rect {{ stroke-width: 2px; stroke: black; fill: white; }}
        #diagram g.edge path {{ stroke: black; stroke-width: 2px; }}
        /* Make nodes clickable */
        #diagram g.node {{ cursor: pointer; }}
    </style>
</head>
<body>
    <div id="diagram">
        {svg_content}
    </div>
    <div id="info-panel">
        <div class="info-title" id="info-title">CLICK A NODE FOR DETAILS</div>
        <div class="info-desc" id="info-desc"></div>
        <div class="info-data" id="info-data"></div>
    </div>
    <script>
        // Add click event listeners to all nodes
        document.addEventListener('DOMContentLoaded', function() {{
            const nodes = document.querySelectorAll('#diagram g.node');
            nodes.forEach(node => {{
                node.addEventListener('click', function() {{
                    const nodeId = this.id.replace('node_', '');
                    showInfo(nodeId);
                }});
            }});
        }});
        
        function showInfo(nodeId) {{
            const info = {node_info_json};
            if (info[nodeId]) {{
                document.getElementById('info-title').textContent = info[nodeId].title;
                document.getElementById('info-desc').textContent = info[nodeId].desc;
                let dataText = info[nodeId].data;
                // Simple text formatting - no regex complexity
                dataText = dataText.replace('Input:', '[INPUT]:');
                dataText = dataText.replace('Output:', '[OUTPUT]:');
                dataText = dataText.replace('API:', '[API]:');
                dataText = dataText.replace('Status:', '[STATUS]:');
                document.getElementById('info-data').textContent = dataText;
            }}
        }}
    </script>
</body>
</html>"""
    
    return html_content

def main():
    """Main function to generate brutalist minimal workflow diagram"""
    figures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'figures')
    os.makedirs(figures_dir, exist_ok=True)
    
    try:
        # Generate brutalist minimal diagram
        dot_brutalist = create_brutalist_minimal_diagram()
        node_info = create_node_info()
        
        # Get SVG content
        svg_content = dot_brutalist.pipe().decode('utf-8')
        
        # Create brutalist HTML wrapper
        html_content = create_brutalist_html_wrapper(svg_content, node_info)
        
        # Save brutalist minimal version
        output_path = os.path.join(figures_dir, 'IPCC_Workflow_Brutalist_Minimal.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f'Brutalist minimal diagram saved to: {os.path.abspath(output_path)}')
        
    except Exception as e:
        print(f'Error generating brutalist diagram: {str(e)}')

if __name__ == "__main__":
    main()
