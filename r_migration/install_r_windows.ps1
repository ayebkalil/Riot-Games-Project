# Install R on Windows using winget (if needed), then print Rscript path.

$ErrorActionPreference = 'Stop'

$rscript = Get-Command Rscript -ErrorAction SilentlyContinue
if ($rscript) {
    Write-Host "Rscript already available:" $rscript.Source
    exit 0
}

$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    Write-Error "winget not found. Install R manually from https://cran.r-project.org/bin/windows/base/"
}

Write-Host "Installing R via winget..."
winget install -e --id RProject.R --accept-package-agreements --accept-source-agreements

$rscriptExe = Get-ChildItem -Path "C:\Program Files\R" -Recurse -Filter "Rscript.exe" -ErrorAction SilentlyContinue |
    Sort-Object FullName -Descending |
    Select-Object -First 1

if ($rscriptExe) {
    Write-Host "Installed Rscript at:" $rscriptExe.FullName
    Write-Host "Use explicit path in this session if PATH is not refreshed yet."
    exit 0
}

Write-Error "R installed but Rscript.exe not found under C:\Program Files\R"
