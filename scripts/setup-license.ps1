$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    & "$PSScriptRoot\setup.ps1"
    $env:SUPABASE_URL = Read-Host 'Supabase project URL (https://PROJECT.supabase.co)'
    $env:SUPABASE_PUBLISHABLE_KEY = Read-Host 'Supabase publishable key (sb_publishable_...)'
    & .\.venv\Scripts\python.exe -m streamlit run license_setup.py
    if ($LASTEXITCODE -ne 0) { throw 'License setup screen exited with an error.' }
} finally {
    Pop-Location
}
