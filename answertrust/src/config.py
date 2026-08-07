"""Shared paths and configuration values for AnswerTrust."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
DATABASE_PATH = DATA_DIR / "answertrust.db"
EVALUATION_EXAMPLES_PATH = DATA_DIR / "evaluation_examples.json"
EXPERIMENT_RESULTS_PATH = RESULTS_DIR / "experiment_results.csv"

MAX_INPUT_CHARS = 5000
MIN_MEANINGFUL_CHARS = 3
