$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$modelCache = Join-Path $projectRoot "model_cache"
New-Item -ItemType Directory -Force -Path $modelCache | Out-Null
$env:HF_HOME = $modelCache

python -c "from src.semantic import SemanticMatcher; model = SemanticMatcher(allow_download=True); print('Embedding dimensions:', model.encoder.get_sentence_embedding_dimension()); print('Model cache:', r'$modelCache')"
