@echo off
cd /d "c:\Users\ayebk\OneDrive\Desktop\hezou\Riot Games Project"
echo ================================================================================
echo Starting Riot Games API Backend
echo ================================================================================
echo.
.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8001
