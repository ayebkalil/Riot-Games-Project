@echo off
REM GitHub Push Script for Riot Games Project
REM Run this from the project root

echo ========================================
echo  GitHub Push Script
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Git status...
git status
echo.

echo [2/4] Verifying commit...
git log --oneline -1
echo.

echo [3/4] Configuring Git for large push...
git config http.postBuffer 524288000
git config http.maxRequestBuffer 100M
git config core.compression 0
git config http.version HTTP/1.1
echo Configuration complete.
echo.

echo [4/4] Pushing to GitHub...
echo This may take several minutes for large repositories.
echo.

git push origin main --progress

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Push completed successfully!
    echo View your repository at:
    echo https://github.com/ayebkalil/riot-project
) else (
    echo FAILED: Push did not complete.
    echo.
    echo Try these alternatives:
    echo 1. Check your internet connection
    echo 2. Visit https://github.com/ayebkalil/riot-project/upload
    echo 3. Use GitHub Desktop application
    echo 4. Contact GitHub Support
)
echo ========================================
echo.

pause
