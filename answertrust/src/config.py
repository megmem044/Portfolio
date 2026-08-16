"""Shared paths and configuration values for AnswerTrust."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
MODEL_CACHE_DIR = PROJECT_ROOT / "model_cache"


def configure_model_cache() -> None:
    """Route Hugging Face and Transformers cache writes into the project."""
    import os

    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = str(MODEL_CACHE_DIR)
    os.environ["HF_HOME"] = cache
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
DATABASE_PATH = DATA_DIR / "answertrust.db"
EVALUATION_EXAMPLES_PATH = DATA_DIR / "evaluation_examples.json"
SEMANTIC_EXAMPLES_PATH = DATA_DIR / "semantic_examples.json"
NLI_EXAMPLES_PATH = DATA_DIR / "nli_examples.json"
EXPERIMENT_RESULTS_PATH = RESULTS_DIR / "experiment_results.csv"
