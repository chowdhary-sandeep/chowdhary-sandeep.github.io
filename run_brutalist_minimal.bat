@echo off
REM Add Graphviz to PATH for this session
set "PATH=%PATH%;C:\Program Files\Graphviz\bin"

REM Run the brutalist minimal workflow diagram script
python create_workflow_diagram_brutalist_minimal.py

REM Keep the window open to see any output
pause
