import graphviz
import os

def create_static_diagrams():
    # Create a new Digraph with higher DPI and adjusted dimensions
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='TB', size='12.1,12.32')  # Reduced height by 20%
    dot.attr('graph', ranksep='0.72', nodesep='0.6')  # Reduced rank separation for more compact layout
    
    # Set default node attributes for square boxes - adjusted font size
    dot.attr('node', shape='box', style='rounded', width='2.4', height='0.8', fontsize='19.6')  # Increased node labels by 40%
    dot.attr('edge', fontsize='19.6')  # Increased edge labels by 40%

    # Status symbols
    done = '✓'  # Green tick
    hard = '⭕'  # Red circle
    medium = '⚠'  # Yellow warning

    # Nodes with status indicators
    dot.node('S', f'Update Search Strategy {medium}\n(OpenAlex metadata)')
    dot.node('L', f'Literature Collector {done}\n(OpenAlex metadata)')
    dot.node('FPC', f'Full Paper Collector {hard}\n(if Open Access)')
    dot.node('ML', f'Zeroshot ML Classifier {done}\n(assigns paper to IPCC sections)')
    dot.node('KIE', f'Key Insight Extractor {done}\n(LLM)')
    dot.node('VAL', f'Validator AI {medium}\n(checks key insights)')
    dot.node('IPCC', f'Live Editor Agent {medium}\n(IPCC HTML)')
    dot.node('PLAC', f'Placement in IPCC {done}')
    dot.node('KG', f'AI-driven Knowledge Graph\nGeneration {hard}')
    dot.node('CE', f'Conceptual Enrichment\n(Latent Information Inference) {hard}')
    dot.node('AT', f'Auto-think Layer for\nClimate Science {hard}')
    dot.node('NS', f'New Science Output {hard}')

    # Create subgraph for main workflow
    with dot.subgraph(name='cluster_0') as main:
        main.attr(label='LIVE-UPDATED IPCC REPORT', labelloc='t', labeljust='c', fontsize='24', fontname='bold')
        # Edges for main workflow
        main.edge('S', 'L', label='update')
        main.edge('L', 'S', label='feedback')
        main.edge('L', 'FPC', label='DOI + metadata')
        main.edge('FPC', 'ML', label='full paper/abstract')
        main.edge('FPC', 'KIE', label='full paper/abstract')
        main.edge('ML', 'PLAC')
        main.edge('KIE', 'PLAC', label='key insights')
        main.edge('KIE', 'VAL', label='key insights')
        main.edge('VAL', 'IPCC', label='validation score')
        main.edge('VAL', 'PLAC', label='validated insights')
        main.edge('PLAC', 'IPCC')

    # Create subgraph for AI knowledge processing with dashed border
    with dot.subgraph(name='cluster_1') as ai:
        ai.attr(style='dashed', color='gray')
        ai.attr(label='AUTO-THINK LAYER FOR NEW SCIENCE', labelloc='t', labeljust='c', fontsize='24', fontname='bold')
        
        # Special nodes for AI processing
        ai.node('KG', 'AI-driven Knowledge Graph\nGeneration')
        ai.node('CE', 'Conceptual Enrichment\n(Latent Information Inference)')
        # Special styling for Auto-think node will be handled in CSS for interactive version
        ai.node('AT', 'Auto-think Layer for\nClimate Science', style='filled', fillcolor='#e6f3ff')
        ai.node('NS', 'New Science Output')

    # Connect main workflow to AI processing
    dot.edge('KIE', 'KG', label='insights')
    dot.edge('KG', 'CE', label='knowledge graph')
    dot.edge('CE', 'AT', label='enriched concepts')
    dot.edge('AT', 'NS', label='novel findings')

    return dot

def create_interactive_diagram():
    dot = graphviz.Digraph(format='svg')
    # Brutalist defaults: square nodes, thick borders; white edges for dark bg
    dot.attr(rankdir='TB', size='12.1,12.32')
    dot.attr('graph', ranksep='0.72', nodesep='0.6', bgcolor='transparent')
    dot.attr('node', shape='box', style='filled', fillcolor='white', color='black', penwidth='3', width='2.4', height='0.8', fontsize='19.6', fontname='Helvetica-Bold', fontcolor='black')
    dot.attr('edge', fontsize='19.6', color='white', penwidth='2', fontname='Helvetica-Bold', fontcolor='white')

    # Status symbols
    done = '✓'  # Green tick
    hard = '⭕'  # Red circle
    medium = '⚠'  # Yellow warning

    # Node descriptions for tooltips and click events
    node_info = {
        'USS': {
            'title': f'Update Search Strategy {medium}',
            'desc': 'Dynamically updates search criteria based on feedback from the Literature Collector.',
            'data': 'Input: Feedback from collector\nOutput: Updated search parameters\nAPI: OpenAlex\nStatus: In Progress (Medium Difficulty)',
            'status': 'medium'
        },
        'LC': {
            'title': f'Literature Collector {done}',
            'desc': 'Collects initial metadata from OpenAlex API including DOI, Open Access status, title, abstract, and year.',
            'data': 'Input: Search parameters\nOutput: Paper metadata\nAPI: OpenAlex\nStatus: Completed',
            'status': 'done'
        },
        'FPC': {
            'title': f'Full Paper Collector {hard}',
            'desc': 'Retrieves full paper content for Open Access papers, otherwise relies on abstract.',
            'data': 'Input: DOI + metadata\nOutput: Full paper or abstract\nStatus: Not Started (High Difficulty)',
            'status': 'hard'
        },
        'KIE': {
            'title': f'Key Insight Extractor {done}',
            'desc': 'Large Language Model that extracts key findings and insights from papers.',
            'data': 'Model: GPT-4/Claude\nInput: Paper text\nOutput: Structured insights\nStatus: Completed',
            'status': 'done'
        },
        'ZC': {
            'title': f'Zeroshot ML Classifier {done}',
            'desc': 'Categorizes papers into relevant IPCC sections using zero-shot classification.',
            'data': 'Input: Paper content\nOutput: IPCC section classifications\nStatus: Completed',
            'status': 'done'
        },
        'VAI': {
            'title': f'Validator AI {medium}',
            'desc': 'Validates extracted insights and additions against original papers and existing knowledge.',
            'data': 'Input: Insights, original abstracts, existing database\nOutput: Validation scores\nStatus: In Progress',
            'status': 'medium'
        },
        'IPCC': {
            'title': f'Placement in IPCC {done}',
            'desc': 'Determines optimal placement of validated content within IPCC structure.',
            'data': 'Input: Validated content\nOutput: Placement recommendations\nStatus: Completed',
            'status': 'done'
        },
        'LEA': {
            'title': f'Live Editor Agent {medium}',
            'desc': 'Manages content integration and works with Validator AI for continuous validation.',
            'data': 'Input: Validated content\nOutput: Updated IPCC content\nStatus: In Progress',
            'status': 'medium'
        },
        'KG': {
            'title': f'AI-driven Knowledge Graph Generation {hard}',
            'desc': 'Constructs a dynamic knowledge graph from extracted insights.',
            'data': 'Input: Insights\nOutput: Knowledge graph\nStatus: Not Started (High Difficulty)',
            'status': 'hard'
        },
        'CE': {
            'title': f'Conceptual Enrichment {hard}',
            'desc': 'Infers relationships from knowledge graph using AI reasoning.',
            'data': 'Input: Knowledge graph\nOutput: Enriched concepts\nStatus: Not Started',
            'status': 'hard'
        },
        'AT': {
            'title': f'Auto-think Layer for Climate Science {hard}',
            'desc': 'Generates new scientific hypotheses from enriched concepts.',
            'data': 'Input: Enriched concepts\nOutput: Novel insights\nStatus: Not Started',
            'status': 'hard'
        },
        'DAP': {
            'title': f'Discovering Adjacent Possible {hard}',
            'desc': 'Explores potential breakthrough areas at the edges of current knowledge.',
            'data': 'Input: Enriched concepts\nOutput: Novel possibilities\nStatus: Not Started',
            'status': 'hard'
        },
        'NS': {
            'title': f'New Science {hard}',
            'desc': 'Novel scientific findings emerging from the knowledge exploration cycle.',
            'data': 'Output: New discoveries\nStatus: Not Started',
            'status': 'hard'
        }
    }

    # Helper function to create node with consistent styling
    def create_styled_node(graph, node_id, info):
        tooltip = f"{info['title']}\n{info['desc']}"
        # Brutalist: white fill, status-colored thick border
        color = 'black'
        if info['status'] == 'done':
            color = '#00ff66'
        elif info['status'] == 'hard':
            color = '#ff0033'
        elif info['status'] == 'medium':
            color = '#ff7a00'
        graph.node(
            node_id,
            info['title'],
            tooltip=tooltip,
            href=f"javascript:showInfo('{node_id}')",
            target="_self",
            style='filled',
            fillcolor='white',
            color=color,
            penwidth='3',
            fontcolor='black'
        )

    # Create subgraph for main workflow
    with dot.subgraph(name='cluster_0') as main:
        main.attr(label='LIVE-UPDATED IPCC REPORT', fontsize='23.4')  # Increased title font
        
        # Create nodes with styling
        for node_id in ['USS', 'LC', 'FPC', 'KIE', 'ZC', 'VAI', 'IPCC', 'LEA']:
            create_styled_node(main, node_id, node_info[node_id])
        main.edge('LC', 'VAI', 'original abstracts\nfor validation', style='dashed')
   
        # Main workflow edges
        main.edge('USS', 'LC', 'update')
        main.edge('LC', 'USS', 'feedback')
        
        # Direct paths using abstracts
        main.edge('LC', 'KIE', 'abstract')
        main.edge('LC', 'ZC', 'abstract')
        
        # Optional full paper collection loop
        main.edge('LC', 'FPC', 'DOI', style='dashed')
        main.edge('FPC', 'LC', 'full paper', style='dashed')
        
        # Rest of the workflow
        main.edge('KIE', 'VAI', 'key insights')
        main.edge('ZC', 'IPCC', 'key insights')
        main.edge('VAI', 'IPCC', 'validated insights')
        main.edge('IPCC', 'LEA', 'validation score')
        
        # Validation feedback loops
        main.edge('LEA', 'VAI', 'added insights', dir='both')

    # Create subgraph for AI processing
    with dot.subgraph(name='cluster_1') as ai:
        ai.attr(label='AUTO-THINK LAYER FOR NEW SCIENCE', fontsize='23.4')  # Increased title font
        ai.attr(margin='50')  # Move contents up
        
        # Create AI nodes with styling
        for node_id in ['KG', 'CE', 'DAP', 'AT', 'NS']:
            create_styled_node(ai, node_id, node_info[node_id])
        
        # AI layer edges - create triangular loop
        ai.edge('KG', 'CE', 'knowledge graph')
        ai.edge('CE', 'DAP', 'enriched concepts')
        ai.edge('DAP', 'AT', 'novel possibilities')
        ai.edge('AT', 'CE', 'new hypotheses', constraint='false')  # Back to CE
        ai.edge('CE', 'AT', 'enriched concepts')  # Bidirectional with AT
        ai.edge('AT', 'DAP', 'exploration paths', constraint='false')  # Back to DAP
        ai.edge('AT', 'NS', 'validated discoveries')  # Final output

    # Connect the layers
    dot.edge('KIE', 'KG', 'insights')
    
    return dot, node_info

def create_html_wrapper(svg_content, node_info):
    import json
    node_info_json = json.dumps(node_info)
    html_content = r"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Interactive IPCC Workflow Diagram</title>
        <style>
            body { font-family: Arial, Helvetica, sans-serif; margin: 0; padding: 16px; display: flex; gap: 16px; background: #000; color: #fff; }
            #diagram { flex: 2; min-width: 70%; border: 3px solid #fff; padding: 8px; }
            #info-panel { flex: 1; max-width: 420px; padding: 12px; border: 3px solid #fff; position: sticky; top: 16px; height: fit-content; background: transparent; }
            .info-section { margin-bottom: 15px; }
            .info-title { font-size: 1.1em; font-weight: 800; color: #fff; text-transform: uppercase; margin-bottom: 10px; }
            .info-desc { color: #b0b0b0; margin-bottom: 15px; }
            .info-data { font-family: monospace; background: #000; color: #fff; border: 3px solid #fff; padding: 10px; white-space: pre-line; line-height: 1.5; }
            .info-data span.io { color: #ffef00; font-weight: bold; }
            .info-data span.status-done { color: #00ff66; font-weight: bold; }
            .info-data span.status-hard { color: #ff0033; font-weight: bold; }
            .info-data span.status-medium { color: #ff7a00; font-weight: bold; }
            .video-link { color: #ffef00; text-decoration: underline; display: inline-block; margin-top: 10px; padding: 6px 10px; border: 3px solid #fff; }
            .video-link:hover { background: #fff; color: #000; text-decoration: none; }
            .video-container { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.98); z-index: 1000; }
            .video-wrapper { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 85%; max-width: 1400px; }
            .back-button { position: absolute; top: 20px; left: 20px; padding: 10px 20px; background-color: #000; color: #fff; border: 3px solid #fff; cursor: pointer; font-size: 16px; }
            #diagram g.cluster text { font-size: 23.4px; font-weight: 800; fill: #ffffff; text-transform: uppercase; }
            #diagram g.node text { font-size: 19.6px; font-weight: 700; fill: #000000; }
            #diagram g.edge text { font-size: 19.6px; fill: #ffffff; }
            #diagram g.node rect { rx: 0; ry: 0; stroke-width: 3px; }
            #diagram g.node { transition: none; }
            #diagram g.node:hover { filter: none; transform: none; }
            #diagram g.node.done rect { stroke: #00ff66; }
            #diagram g.node.hard rect { stroke: #ff0033; }
            #diagram g.node.medium rect { stroke: #ff7a00; }
        </style>
        <script>
            // Bind click handlers to SVG nodes to open details on the right
            document.addEventListener('DOMContentLoaded', function() {
                try {
                    // Clicks on <a> links inside nodes (preferred)
                    const links = document.querySelectorAll('#diagram g.node a');
                    links.forEach(a => {
                        a.addEventListener('click', function(e) {
                            e.preventDefault();
                            const href = this.getAttribute('xlink:href') || this.getAttribute('href');
                            const m = href && href.match(/showInfo\(['"]([^'"]+)['"]\)/);
                            if (m) { try { showInfo(m[1]); } catch (_) {} }
                        });
                    });

                    const nodeGroups = document.querySelectorAll('#diagram g.node');
                    nodeGroups.forEach(g => {
                        g.style.cursor = 'pointer';
                        g.addEventListener('click', function(e) {
                            e.preventDefault();
                            // Prefer parsing the node id from the embedded <a href="javascript:showInfo('ID')">
                            let nodeId = null;
                            const link = g.querySelector('a');
                            if (link) {
                                const href = link.getAttribute('xlink:href') || link.getAttribute('href');
                                const m = href && href.match(/showInfo\(['"]([^'"]+)['"]\)/);
                                if (m) nodeId = m[1];
                            }
                            // Fallback: try the <title> tag inside the node group (often holds the node name)
                            if (!nodeId) {
                                const titleEl = g.querySelector('title');
                                if (titleEl) nodeId = (titleEl.textContent || '').trim();
                            }
                            if (nodeId) {
                                try { showInfo(nodeId); } catch (_) {}
                            }
                        });
                    });
                } catch (_) {}
            });

            function showInfo(nodeId) {
                const info = __NODE_INFO__;
                document.getElementById('info-title').textContent = info[nodeId].title;
                document.getElementById('info-desc').textContent = info[nodeId].desc;
                let dataText = info[nodeId].data;
                dataText = dataText.replace(/(Input:|Output:)/g, '<span class=\"io\">$1</span>');
                if (dataText.includes('Status: Completed')) {
                    dataText = dataText.replace(/Status: Completed/g, '<span class=\"status-done\">Status: Completed</span>');
                } else if (dataText.includes('Status: Not Started')) {
                    dataText = dataText.replace(/Status: Not Started \\(High Difficulty\\)/g, '<span class=\"status-hard\">Status: Not Started (High Difficulty)</span>');
                } else if (dataText.includes('Status: In Progress')) {
                    dataText = dataText.replace(/Status: In Progress/g, '<span class=\"status-medium\">Status: In Progress</span>');
                }
                document.getElementById('info-data').innerHTML = dataText;
                const videoLinkContainer = document.getElementById('video-link-container');
                if (nodeId === 'LC') {
                    videoLinkContainer.innerHTML = '<a href=\"#\" class=\"video-link\" onclick=\"showVideo(); return false;\">Watch Demo Video</a>';
                } else {
                    videoLinkContainer.innerHTML = '';
                }
            }
            function showVideo() {
                const videoContainer = document.getElementById('video-container');
                videoContainer.style.display = 'block';
                videoContainer.innerHTML = `
                    <button class="back-button" onclick="hideVideo()">← Back to Diagram</button>
                    <div class="video-wrapper">
                        <video width="100%" controls autoplay>
                            <source src="systematic_review 3.mp4" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                `;
            }
            function hideVideo() {
                const videoContainer = document.getElementById('video-container');
                videoContainer.style.display = 'none';
                videoContainer.innerHTML = '';
            }
        </script>
    </head>
    <body>
        <div id="diagram">
            __SVG__
        </div>
        <div id="info-panel">
            <div class="info-section">
                <div class="info-title" id="info-title">Click a node to see details</div>
                <div class="info-desc" id="info-desc"></div>
                <div class="info-data" id="info-data"></div>
                <div id="video-link-container"></div>
            </div>
        </div>
        <div id="video-container" class="video-container"></div>
    </body>
    </html>
    """
    return html_content.replace("__NODE_INFO__", node_info_json).replace("__SVG__", svg_content)

def main():
    # Create figures directory if it doesn't exist
    figures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'figures')
    os.makedirs(figures_dir, exist_ok=True)

    try:
        # Generate interactive version only
        dot_interactive, node_info = create_interactive_diagram()
        svg_path = os.path.join(figures_dir, 'Workflow_Diagram_interactive')
        svg_content = dot_interactive.pipe().decode('utf-8')
        
        # Create HTML with embedded diagram
        html_content = create_html_wrapper(svg_content, node_info)
        
        # Save interactive HTML version
        with open(f'{svg_path}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
            print(f'Interactive diagram has been saved to: {os.path.abspath(f.name)}')
            
    except Exception as e:
        print(f'Error generating diagrams: {str(e)}')

if __name__ == "__main__":
    main() 