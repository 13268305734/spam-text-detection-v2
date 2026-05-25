from __future__ import annotations
import argparse
import json
from .model import train_model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/sample_comments.csv")
    parser.add_argument("--model", default="models/tfidf_lr.joblib")
    parser.add_argument("--report", default="reports/metrics.json")
    args = parser.parse_args()

    metrics = train_model(args.data, args.model, args.report)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
