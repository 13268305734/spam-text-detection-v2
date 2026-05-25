from __future__ import annotations
import argparse
import json
from .bert_model import TransformerConfig, train_transformer

def main():
    parser = argparse.ArgumentParser(description="Fine-tune BERT/RoBERTa for spam text detection.")
    parser.add_argument("--data", default="data/sample_comments.csv")
    parser.add_argument("--model_name_or_path", default="hfl/chinese-roberta-wwm-ext")
    parser.add_argument("--output_dir", default="models/roberta_spam")
    parser.add_argument("--max_length", type=int, default=128)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=2e-5)
    parser.add_argument("--fp16", action="store_true")
    args = parser.parse_args()

    cfg = TransformerConfig(
        model_name_or_path=args.model_name_or_path,
        output_dir=args.output_dir,
        max_length=args.max_length,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        fp16=args.fp16,
    )
    report = train_transformer(args.data, cfg)
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
