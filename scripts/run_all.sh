#!/usr/bin/env bash
set -e

python -m spam_detector.make_dataset
python -m spam_detector.train --data data/sample_comments.csv --model models/tfidf_lr.joblib --report reports/metrics.json
python -m spam_detector.evaluate --data data/sample_comments.csv --model models/tfidf_lr.joblib --out reports/ensemble_metrics.json
python -m spam_detector.predict --text "加薇信免费领取资料，数量有限！"
