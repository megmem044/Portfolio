$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$streamlitProfile = Join-Path $projectRoot ".streamlit-profile"
$streamlitConfig = Join-Path $streamlitProfile ".streamlit"

New-Item -ItemType Directory -Force -Path $streamlitConfig | Out-Null
$env:USERPROFILE = $streamlitProfile

python -m streamlit run (Join-Path $projectRoot "app.py") `
    --browser.gatherUsageStats false `
    --server.headless true
