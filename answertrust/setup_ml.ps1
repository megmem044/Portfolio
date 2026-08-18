# Download and cache the local embedding and NLI models.
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$modelCache = Join-Path $projectRoot "model_cache"
New-Item -ItemType Directory -Force -Path $modelCache | Out-Null
$env:HF_HOME = $modelCache

python -c "from src.semantic import SemanticMatcher; model = SemanticMatcher(allow_download=True); print('Embedding dimensions:', model.encoder.get_sentence_embedding_dimension()); from src.nli import NLIClassifier; nli=NLIClassifier(allow_download=True); print('NLI check:', nli.predict('Treatment did not improve sleep.', 'Treatment improved sleep.')); print('Model cache:', r'$modelCache')"
