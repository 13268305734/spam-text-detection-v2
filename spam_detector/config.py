from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"

LABEL_NORMAL = 0
LABEL_SPAM = 1

RANDOM_SEED = 42

# Ensemble weights. Keep them explicit so they can be tuned in ablation studies.
RULE_WEIGHT = 0.30
MODEL_WEIGHT = 0.50
VARIANT_WEIGHT = 0.20

DEFAULT_THRESHOLD = 0.50
