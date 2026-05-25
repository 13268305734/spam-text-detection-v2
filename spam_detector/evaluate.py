from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from .model import load_model
from .ensemble import explain_prediction

def evaluate(data_path: str, model_path: str, threshold: float = 0.5):
    df = pd.read_csv(data_path)
    model = load_model(model_path)
    preds = []
    for text in df["text"].astype(str):
        out = explain_prediction(text, model=model, threshold=threshold)
        preds.append(out["label"])
    y = df["label"].astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y, preds, average="binary", zero_division=0)
    return {
        "accuracy": float(accuracy_score(y, preds)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": confusion_matrix(y, preds).tolist(),
        "n": int(len(df)),
        "threshold": threshold,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/sample_comments.csv")
    parser.add_argument("--model", default="models/tfidf_lr.joblib")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--out", default="reports/ensemble_metrics.json")
    args = parser.parse_args()
    metrics = evaluate(args.data, args.model, args.threshold)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
