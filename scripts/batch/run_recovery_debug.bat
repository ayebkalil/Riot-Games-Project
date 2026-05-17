@echo off
setlocal enabledelayedexpansion
cd /d "c:\Users\ayebk\OneDrive\Desktop\hezou\Riot Games Project"
echo [DEBUG] Current directory: %CD%
echo [DEBUG] Python executable:
.venv\Scripts\python.exe --version
echo [DEBUG] Running recovery script...
.venv\Scripts\python.exe recover_models.py 2>&1
echo [DEBUG] Script exit code: %ERRORLEVEL%
pause
