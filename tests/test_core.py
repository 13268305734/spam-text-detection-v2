from spam_detector.similarity import normalize_variants, suspicious_keywords
from spam_detector.rules import rule_score
from spam_detector.ensemble import explain_prediction


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


def test_normal_context_reduces_false_positive_risk():
    spam = explain_prediction("加微信免费领取资料", model=None)
    normal_context = explain_prediction("微信小程序开发需要配置支付接口环境", model=None)

    assert normal_context["risk_score"] < spam["risk_score"]
    assert normal_context["review_status"] == "通过"
    assert any("正常语境" in reason for reason in normal_context["reasons"])


def test_prediction_includes_spam_categories():
    out = explain_prediction("加vx私聊返现，扫码进群领红包", model=None)

    assert "联系方式引流" in out["risk_categories"]
    assert "优惠返现" in out["risk_categories"]
    assert "群聊导流" in out["risk_categories"]


def test_borderline_prediction_requires_manual_review():
    out = explain_prediction("加微信", model=None)

    assert out["review_status"] == "建议人工复核"
