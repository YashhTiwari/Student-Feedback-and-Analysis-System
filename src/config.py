"""Common paths and settings for the whole project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
OUT_DIR = ROOT / "outputs"

RAW_CSV = DATA_DIR / "feedback.csv"
CLEAN_CSV = DATA_DIR / "feedback_clean.csv"
MODEL_PATH = MODEL_DIR / "sentiment_model.pkl"

RANDOM_STATE = 42

for d in (DATA_DIR, MODEL_DIR, OUT_DIR):
    d.mkdir(exist_ok=True)
