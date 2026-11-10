$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Unable to create the virtual environment.' }
    }
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    & .\.venv\Scripts\python.exe -m playwright install chromium
    if ($LASTEXITCODE -ne 0) { throw 'Chromium installation failed. Rerun setup to retry.' }
    Write-Host 'Setup complete. Run: .\scripts\run.ps1'
} finally {
    Pop-Location
}
