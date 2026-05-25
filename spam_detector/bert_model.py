from __future__ import annotations

"""Optional BERT/RoBERTa module.

This module is intentionally optional because pretrained Transformer weights are
large and should not be committed into a course-project zip. When the user has
internet access or a local HuggingFace cache, it can train/fine-tune:
- bert-base-chinese
- hfl/chinese-roberta-wwm-ext
- hfl/chinese-macbert-base
or any compatible sequence-classification checkpoint.

The rest of the project continues to run without torch/transformers.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import random

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from .config import RANDOM_SEED


@dataclass
class TransformerConfig:
    model_name_or_path: str = "hfl/chinese-roberta-wwm-ext"
    output_dir: str = "models/roberta_spam"
    max_length: int = 128
    epochs: int = 3
    batch_size: int = 16
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    test_size: float = 0.2
    warmup_ratio: float = 0.1
    fp16: bool = False


def _require_transformers():
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except Exception as exc:
        raise ImportError(
            "BERT/RoBERTa support requires extra dependencies. Install with:\n"
            "pip install torch transformers accelerate datasets\n"
            "If the environment cannot access HuggingFace, download the model "
            "manually and pass --model_name_or_path /path/to/local/checkpoint."
        ) from exc


class SpamTextDataset:
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 128):
        _require_transformers()
        import torch
        self.texts = [str(x) for x in texts]
        self.labels = [int(x) for x in labels]
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.torch = torch

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        item = {k: v.squeeze(0) for k, v in enc.items()}
        item["labels"] = self.torch.tensor(self.labels[idx], dtype=self.torch.long)
        return item


def train_transformer(data_path: str | Path, cfg: TransformerConfig) -> Dict[str, Any]:
    """Fine-tune a Chinese BERT/RoBERTa style classifier.

    CSV format:
        text,label
        这个课程讲得很清楚,0
        加微信领取优惠券,1
    """
    _require_transformers()
    import torch
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        TrainingArguments,
        Trainer,
        set_seed,
    )

    set_seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    df = pd.read_csv(data_path).dropna(subset=["text", "label"]).copy()
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)

    train_df, test_df = train_test_split(
        df,
        test_size=cfg.test_size,
        random_state=RANDOM_SEED,
        stratify=df["label"],
    )

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name_or_path)
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg.model_name_or_path,
        num_labels=2,
    )

    train_ds = SpamTextDataset(
        train_df["text"].tolist(), train_df["label"].tolist(), tokenizer, cfg.max_length
    )
    test_ds = SpamTextDataset(
        test_df["text"].tolist(), test_df["label"].tolist(), tokenizer, cfg.max_length
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = logits.argmax(axis=-1)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, preds, average="binary", zero_division=0
        )
        return {
            "accuracy": accuracy_score(labels, preds),
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    args = TrainingArguments(
        output_dir=cfg.output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=cfg.learning_rate,
        per_device_train_batch_size=cfg.batch_size,
        per_device_eval_batch_size=cfg.batch_size,
        num_train_epochs=cfg.epochs,
        weight_decay=cfg.weight_decay,
        warmup_ratio=cfg.warmup_ratio,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=20,
        save_total_limit=2,
        fp16=cfg.fp16 and torch.cuda.is_available(),
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    metrics = trainer.evaluate()

    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))

    # Manual predictions for confusion matrix.
    pred_out = trainer.predict(test_ds)
    preds = pred_out.predictions.argmax(axis=-1)
    labels = test_df["label"].to_numpy()
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="binary", zero_division=0
    )
    report = {
        "model_name_or_path": cfg.model_name_or_path,
        "output_dir": str(out_dir),
        "n_train": int(len(train_df)),
        "n_test": int(len(test_df)),
        "accuracy": float(accuracy_score(labels, preds)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "confusion_matrix": confusion_matrix(labels, preds).tolist(),
        "trainer_metrics": {k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))},
    }
    (out_dir / "eval_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def load_transformer_model(model_dir: str | Path):
    """Load a fine-tuned Transformer checkpoint."""
    _require_transformers()
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    model_dir = str(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    return {"tokenizer": tokenizer, "model": model, "device": device, "torch": torch}


def predict_transformer(bundle, texts: List[str], max_length: int = 128) -> List[float]:
    """Return spam probabilities for texts."""
    tokenizer = bundle["tokenizer"]
    model = bundle["model"]
    device = bundle["device"]
    torch = bundle["torch"]

    probs: List[float] = []
    with torch.no_grad():
        for text in texts:
            enc = tokenizer(
                str(text),
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors="pt",
            )
            enc = {k: v.to(device) for k, v in enc.items()}
            logits = model(**enc).logits
            prob = torch.softmax(logits, dim=-1)[0, 1].item()
            probs.append(float(prob))
    return probs
