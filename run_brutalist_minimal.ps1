# Add Graphviz to PATH for this session
$env:PATH += ";C:\Program Files\Graphviz\bin"

# Run the brutalist minimal workflow diagram script
python create_workflow_diagram_brutalist_minimal.py

# Keep the window open to see any output
Read-Host "Press Enter to continue..."
