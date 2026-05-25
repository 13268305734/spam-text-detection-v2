#!/usr/bin/env bash
set -e

# 需要联网或提前准备好本地 HuggingFace checkpoint。
python -m spam_detector.train_transformer   --data data/sample_comments.csv   --model_name_or_path hfl/chinese-roberta-wwm-ext   --output_dir models/roberta_spam   --epochs 3   --batch_size 16   --learning_rate 2e-5
