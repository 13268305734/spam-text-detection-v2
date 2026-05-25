from __future__ import annotations
import argparse
import json
from pathlib import Path
from .ensemble import explain_prediction
from .model import load_model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True, help="Input text to classify")
    parser.add_argument("--model", default="models/tfidf_lr.joblib", help="Path to trained model")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    model = None
    if Path(args.model).exists():
        model = load_model(args.model)
    result = explain_prediction(args.text, model=model, threshold=args.threshold)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
