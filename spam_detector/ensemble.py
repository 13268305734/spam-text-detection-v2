from __future__ import annotations
from typing import Dict, Any, Optional
from .config import RULE_WEIGHT, MODEL_WEIGHT, VARIANT_WEIGHT, DEFAULT_THRESHOLD
from .rules import rule_score
from .similarity import variant_score, normalize_variants
from .risk_analysis import (
    apply_context_suppression,
    infer_risk_categories,
    review_status,
    risk_keywords,
)

def fuse_score(rule: float, model: Optional[float], variant: float) -> float:
    if model is None:
        # When no trained model is available, re-normalize rule/variant weights.
        denom = RULE_WEIGHT + VARIANT_WEIGHT
        return min((RULE_WEIGHT * rule + VARIANT_WEIGHT * variant) / denom, 1.0)
    return min(RULE_WEIGHT * rule + MODEL_WEIGHT * model + VARIANT_WEIGHT * variant, 1.0)

def explain_prediction(text: str, model=None, threshold: float = DEFAULT_THRESHOLD) -> Dict[str, Any]:
    r_score, r_reasons, r_features = rule_score(text)
    v_score, v_reasons = variant_score(text)
    m_score = None
    if model is not None:
        from .model import predict_proba
        m_score = predict_proba(model, [text])[0]

    score = fuse_score(r_score, m_score, v_score)
    score, context_reasons = apply_context_suppression(score, text)
    reasons = []
    reasons.extend(r_reasons)
    reasons.extend(v_reasons)
    reasons.extend(context_reasons)
    if m_score is not None:
        reasons.append(f"机器学习模型垃圾概率：{m_score:.3f}")
    if not reasons:
        reasons.append("未命中明显风险规则，模型风险较低")
    keywords = risk_keywords(text)
    categories = infer_risk_categories(r_features, keywords)
    label = int(score >= threshold)

    return {
        "text": text,
        "normalized_text": normalize_variants(text),
        "label": label,
        "label_name": "垃圾文本" if label else "正常文本",
        "risk_score": round(float(score), 4),
        "rule_score": round(float(r_score), 4),
        "model_score": None if m_score is None else round(float(m_score), 4),
        "variant_score": round(float(v_score), 4),
        "threshold": threshold,
        "review_status": review_status(score, threshold, categories),
        "risk_categories": categories,
        "keywords": keywords,
        "reasons": reasons,
        "rule_features": r_features,
    }
