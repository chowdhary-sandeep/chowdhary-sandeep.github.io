@echo off
echo IPCC AR7 Chapter 5: Enablers and Barriers - Seed Paper Search
echo ================================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Python found. Checking required packages...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo.
echo All requirements satisfied. Starting search...
echo.
echo This will search for seed papers across all 15 IPCC topics.
echo The process may take 30-60 minutes depending on network conditions.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Starting IPCC seed paper search...
python main_orchestrator.py

echo.
echo Search completed. Check the IPCC_AR7_seed folder for results.
echo.
pause
