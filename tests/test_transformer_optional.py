def test_bert_module_imports_without_transformer_runtime():
    import spam_detector.bert_model as bm
    cfg = bm.TransformerConfig()
    assert cfg.max_length == 128
    assert "roberta" in cfg.model_name_or_path.lower()
