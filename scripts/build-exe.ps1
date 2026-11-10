$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    & .\.venv\Scripts\python.exe -m pip install 'pyinstaller>=6.22.1,<7'
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller installation failed.' }
    & .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --console --name SocialPostTool --paths src --add-data 'app.py;.' --add-data 'license_setup.py;.' --collect-all streamlit --collect-submodules social_poster --collect-all keyring --copy-metadata playwright --copy-metadata streamlit desktop_launcher.py
    if ($LASTEXITCODE -ne 0) { throw 'EXE build failed.' }
} finally {
    Pop-Location
}
