"""Shared paths and configuration values for AnswerTrust."""

from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", "1048576"))
MAX_QUESTION_LENGTH = int(os.getenv("MAX_QUESTION_LENGTH", "2000"))
MAX_PAPER_LENGTH = int(os.getenv("MAX_PAPER_LENGTH", "500000"))
MAX_ANSWER_LENGTH = int(os.getenv("MAX_ANSWER_LENGTH", "20000"))
EVALUATION_RATE_LIMIT = int(os.getenv("EVALUATION_RATE_LIMIT", "30"))
EVALUATION_RATE_WINDOW_SECONDS = int(
    os.getenv("EVALUATION_RATE_WINDOW_SECONDS", "60")
)
MAX_QUEUED_EVALUATIONS = int(os.getenv("MAX_QUEUED_EVALUATIONS", "100"))
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
DISAGREEMENT_RESULTS_PATH = RESULTS_DIR / "benchmark_disagreements.csv"
