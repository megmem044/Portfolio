$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$streamlitProfile = Join-Path $projectRoot ".streamlit-profile"
$streamlitConfig = Join-Path $streamlitProfile ".streamlit"
$modelCache = Join-Path $projectRoot "model_cache"

New-Item -ItemType Directory -Force -Path $streamlitConfig | Out-Null
New-Item -ItemType Directory -Force -Path $modelCache | Out-Null
$env:USERPROFILE = $streamlitProfile
$env:HF_HOME = $modelCache

python -m streamlit run (Join-Path $projectRoot "app.py") `
    --browser.gatherUsageStats false `
    --server.headless true
