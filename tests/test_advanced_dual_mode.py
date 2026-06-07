import app_advanced


def _stub_common_scores(monkeypatch):
    monkeypatch.setattr(app_advanced, "rule_score", lambda text: (0.0, [], {}))
    monkeypatch.setattr(app_advanced, "variant_score", lambda text: (0.0, []))
    monkeypatch.setattr(app_advanced, "load_optional_transformer", lambda path: (object(), None))
    monkeypatch.setattr(app_advanced, "transformer_probability", lambda bundle, text: 0.8)


def test_dual_model_skips_tfidf_for_non_chinese(monkeypatch):
    _stub_common_scores(monkeypatch)

    def fail_if_loaded():
        raise AssertionError("TF-IDF should not be loaded for non-Chinese text")

    monkeypatch.setattr(app_advanced, "load_tfidf_model", fail_if_loaded)

    out = app_advanced.make_prediction(
        "Claim your free prize now",
        threshold=0.5,
        model_mode="TF-IDF + RoBERTa 双模型",
        transformer_dir="test-roberta",
    )

    assert out["tfidf_score"] is None
    assert out["transformer_score"] == 0.8
    assert out["model_score"] == 0.8
    assert any("跳过 TF-IDF/LR" in reason for reason in out["reasons"])


def test_dual_model_averages_scores_for_chinese(monkeypatch):
    _stub_common_scores(monkeypatch)
    monkeypatch.setattr(app_advanced, "load_tfidf_model", lambda: object())
    monkeypatch.setattr(app_advanced, "tfidf_probability", lambda model, text: 0.2)

    out = app_advanced.make_prediction(
        "点击链接领取优惠",
        threshold=0.5,
        model_mode="TF-IDF + RoBERTa 双模型",
        transformer_dir="test-roberta",
    )

    assert out["tfidf_score"] == 0.2
    assert out["transformer_score"] == 0.8
    assert out["model_score"] == 0.5


def test_dual_model_skips_tfidf_for_mixed_language(monkeypatch):
    _stub_common_scores(monkeypatch)

    def fail_if_loaded():
        raise AssertionError("TF-IDF should not be loaded for mixed-language text")

    monkeypatch.setattr(app_advanced, "load_tfidf_model", fail_if_loaded)

    out = app_advanced.make_prediction(
        "点击 link 领取优惠",
        threshold=0.5,
        model_mode="TF-IDF + RoBERTa 双模型",
        transformer_dir="test-roberta",
    )

    assert out["tfidf_score"] is None
    assert out["model_score"] == 0.8


def test_non_chinese_does_not_fallback_to_tfidf_when_roberta_fails(monkeypatch):
    monkeypatch.setattr(app_advanced, "rule_score", lambda text: (0.0, [], {}))
    monkeypatch.setattr(app_advanced, "variant_score", lambda text: (0.0, []))
    monkeypatch.setattr(
        app_advanced,
        "load_optional_transformer",
        lambda path: (None, "checkpoint unavailable"),
    )

    def fail_if_loaded():
        raise AssertionError("TF-IDF should not be used as a non-Chinese fallback")

    monkeypatch.setattr(app_advanced, "load_tfidf_model", fail_if_loaded)

    out = app_advanced.make_prediction(
        "Claim your free prize now",
        threshold=0.5,
        model_mode="TF-IDF + RoBERTa 双模型",
        transformer_dir="missing-roberta",
    )

    assert out["tfidf_score"] is None
    assert out["transformer_score"] is None
    assert out["model_score"] is None
    assert any("RoBERTa 未启用" in reason for reason in out["reasons"])
