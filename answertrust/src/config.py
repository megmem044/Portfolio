"""Shared paths and configuration values for AnswerTrust."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
MODEL_CACHE_DIR = PROJECT_ROOT / "model_cache"
DATABASE_PATH = DATA_DIR / "answertrust.db"
EVALUATION_EXAMPLES_PATH = DATA_DIR / "evaluation_examples.json"
SEMANTIC_EXAMPLES_PATH = DATA_DIR / "semantic_examples.json"
EXPERIMENT_RESULTS_PATH = RESULTS_DIR / "experiment_results.csv"
