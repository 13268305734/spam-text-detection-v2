from spam_detector.similarity import normalize_variants, suspicious_keywords
from spam_detector.rules import rule_score
from spam_detector.ensemble import explain_prediction
from spam_detector.preprocess import is_all_chinese_text

def test_variant_normalization():
    assert "微信" in normalize_variants("加 薇 信")
    assert "微信" in normalize_variants("加vx")

def test_keywords():
    hits = suspicious_keywords("加薇信免费领取资料")
    assert "微信" in hits or "加微信" in hits

def test_rule_score_spam():
    score, reasons, features = rule_score("加薇信免费领取资料")
    assert score > 0.2
    assert reasons

def test_explain_without_model():
    out = explain_prediction("这个课程讲得很清楚", model=None)
    assert "risk_score" in out
    assert out["label"] in (0, 1)

def test_all_chinese_text():
    assert is_all_chinese_text("这个课程讲得很清楚。")
    assert is_all_chinese_text("课程 123：模型训练！")
    assert not is_all_chinese_text("中文 mixed text")
    assert not is_all_chinese_text("English only")
