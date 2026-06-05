from __future__ import annotations
from pathlib import Path
import html
import json
import re
from typing import List

import pandas as pd
import streamlit as st

from spam_detector.ensemble import explain_prediction, fuse_score
from spam_detector.model import load_model
from spam_detector.rules import rule_score
from spam_detector.similarity import variant_score, normalize_variants, suspicious_keywords

st.set_page_config(
    page_title="高级互联网垃圾文本检测系统",
    page_icon="🛡️",
    layout="wide",
)

TFIDF_MODEL_PATH = Path("models/tfidf_lr.joblib")
DEFAULT_TRANSFORMER_DIR = "kudouKID/mroberta-spam-v2"

@st.cache_resource(show_spinner=False)
def load_tfidf_model():
    return load_model(TFIDF_MODEL_PATH) if TFIDF_MODEL_PATH.exists() else None

@st.cache_resource(show_spinner=False)
def load_optional_transformer(model_dir: str):
    try:
        from spam_detector.bert_model import load_transformer_model
        # Check if the input is a local path or a huggingface hub id
        path = Path(model_dir)
        if path.exists() or "/" in model_dir:
            return load_transformer_model(model_dir), None
        else:
            return None, f"未找到 Transformer checkpoint：{path}"
    except Exception as exc:
        return None, str(exc)

def tfidf_probability(model, text: str):
    if model is None:
        return None
    from spam_detector.model import predict_proba
    return predict_proba(model, [text])[0]

def transformer_probability(bundle, text: str):
    if bundle is None:
        return None
    from spam_detector.bert_model import predict_transformer
    return predict_transformer(bundle, [text])[0]

def make_prediction(text: str, threshold: float, model_mode: str, transformer_dir: str):
    tfidf_model = load_tfidf_model()
    transformer_bundle = None
    transformer_error = None

    r_score, r_reasons, _ = rule_score(text)
    v_score, v_reasons = variant_score(text)
    tfidf_score = tfidf_probability(tfidf_model, text)
    transformer_score = None

    if model_mode in ["Transformer/RoBERTa 优先", "TF-IDF + Transformer 双模型"]:
        transformer_bundle, transformer_error = load_optional_transformer(transformer_dir)
        transformer_score = transformer_probability(transformer_bundle, text) if transformer_bundle else None

    if model_mode == "仅规则+变体":
        model_score = None
    elif model_mode == "Transformer/RoBERTa 优先":
        model_score = transformer_score if transformer_score is not None else tfidf_score
    elif model_mode == "TF-IDF + Transformer 双模型":
        vals = [x for x in [tfidf_score, transformer_score] if x is not None]
        model_score = sum(vals) / len(vals) if vals else None
    else:
        model_score = tfidf_score

    risk_score = fuse_score(r_score, model_score, v_score)
    label = int(risk_score >= threshold)

    reasons = []
    reasons.extend(r_reasons)
    reasons.extend(v_reasons)
    if tfidf_score is not None:
        reasons.append(f"TF-IDF/LR 模型垃圾概率：{tfidf_score:.3f}")
    if transformer_score is not None:
        reasons.append(f"Transformer/RoBERTa 模型垃圾概率：{transformer_score:.3f}")
    if transformer_error and model_mode != "TF-IDF/LR":
        reasons.append("Transformer 未启用：" + transformer_error.split("\n")[0])
    if not reasons:
        reasons.append("未命中明显风险信号")

    return {
        "text": text,
        "normalized_text": normalize_variants(text),
        "label": label,
        "label_name": "垃圾文本" if label else "正常文本",
        "risk_score": round(float(risk_score), 4),
        "rule_score": round(float(r_score), 4),
        "variant_score": round(float(v_score), 4),
        "tfidf_score": None if tfidf_score is None else round(float(tfidf_score), 4),
        "transformer_score": None if transformer_score is None else round(float(transformer_score), 4),
        "model_mode": model_mode,
        "threshold": threshold,
        "reasons": reasons,
        "keywords": suspicious_keywords(text),
    }

def highlight_text(text: str, keywords: List[str]) -> str:
    safe = html.escape(text)
    # Also highlight variant-normalized key characters in raw text.
    raw_terms = set(keywords)
    raw_terms.update(["微信", "薇信", "vx", "wx", "返现", "优惠", "扫码", "进群", "私聊", "免费", "领取"])
    raw_terms = sorted([t for t in raw_terms if t], key=len, reverse=True)
    for term in raw_terms:
        safe = re.sub(
            re.escape(html.escape(term)),
            f"<mark>{html.escape(term)}</mark>",
            safe,
            flags=re.I,
        )
    return safe

st.title("🛡️ 高级互联网垃圾文本检测系统")
st.caption("支持：规则解释、变体归一化、TF-IDF/LR、可选 BERT/RoBERTa、批量检测、风险可视化")

with st.sidebar:
    st.header("检测配置")
    model_mode = st.selectbox(
        "模型模式",
        ["TF-IDF/LR", "Transformer/RoBERTa 优先", "TF-IDF + Transformer 双模型", "仅规则+变体"],
        index=0,
    )
    threshold = st.slider("风险阈值", 0.0, 1.0, 0.50, 0.01)
    transformer_dir = st.text_input("Transformer 目录或云端模型名称", value=str(DEFAULT_TRANSFORMER_DIR))
    st.info("未训练 RoBERTa checkpoint 时，系统会自动回退到 TF-IDF/LR 或规则检测。")

examples = [
    "这个课程讲得挺清楚的，案例也很实用。",
    "加薇信免费领取资料，数量有限！",
    "加 v 信 领·取 优 惠，先到先得",
    "私 聊 我 返·现，扫码进群领红包",
    "微信小程序开发需要配置环境。",
]

tab_single, tab_batch, tab_compare, tab_train = st.tabs([
    "单条检测",
    "批量检测",
    "模型对比",
    "训练说明",
])

with tab_single:
    if "single_text_area" not in st.session_state:
        st.session_state["single_text_area"] = examples[1]

    col_a, col_b = st.columns([2, 1])
    with col_a:
        text = st.text_area("输入文本", key="single_text_area", height=150)
    with col_b:
        st.write("示例")
        chosen = st.radio("选择一条示例", examples, index=1, label_visibility="collapsed")
        
        def set_example_text(val):
            st.session_state["single_text_area"] = val
            
        st.button("填入示例", on_click=set_example_text, args=(chosen,))

    if st.button("开始检测", type="primary"):
        result = make_prediction(text, threshold, model_mode, transformer_dir)
        st.session_state["advanced_single_result"] = result

    if "advanced_single_result" in st.session_state:
        result = st.session_state["advanced_single_result"]
        st.subheader("检测结果")
        if result["label"] == 1:
            st.error(f"{result['label_name']}，风险分数：{result['risk_score']:.3f}")
        else:
            st.success(f"{result['label_name']}，风险分数：{result['risk_score']:.3f}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("规则分数", result["rule_score"])
        c2.metric("变体分数", result["variant_score"])
        c3.metric("TF-IDF/LR", "N/A" if result["tfidf_score"] is None else result["tfidf_score"])
        c4.metric("Transformer", "N/A" if result["transformer_score"] is None else result["transformer_score"])

        st.progress(min(result["risk_score"], 1.0))

        st.markdown("**原文本高亮：**")
        st.markdown(highlight_text(result["text"], result["keywords"]), unsafe_allow_html=True)

        st.markdown("**变体归一化文本：**")
        st.code(result["normalized_text"], language="text")

        st.markdown("**命中原因：**")
        for reason in result["reasons"]:
            st.write("- " + reason)

        with st.expander("查看完整 JSON"):
            st.json(result)

with tab_batch:
    st.subheader("批量检测")
    st.write("上传 CSV，至少包含 `text` 列；如包含 `label` 列，会显示简单评估。")
    uploaded = st.file_uploader("上传 CSV", type=["csv"])
    demo_df = pd.DataFrame({"text": examples})
    use_demo = st.button("使用内置示例批量检测")

    df = None
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    elif use_demo:
        df = demo_df

    if df is not None:
        if "text" not in df.columns:
            st.error("CSV 必须包含 text 列")
        else:
            rows = []
            for text_i in df["text"].astype(str).tolist():
                out = make_prediction(text_i, threshold, model_mode, transformer_dir)
                rows.append({
                    "text": text_i,
                    "pred_label": out["label"],
                    "label_name": out["label_name"],
                    "risk_score": out["risk_score"],
                    "rule_score": out["rule_score"],
                    "variant_score": out["variant_score"],
                    "tfidf_score": out["tfidf_score"],
                    "transformer_score": out["transformer_score"],
                    "reasons": "；".join(out["reasons"][:3]),
                })
            out_df = pd.DataFrame(rows)
            st.dataframe(out_df, use_container_width=True)
            st.download_button(
                "下载检测结果 CSV",
                out_df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="spam_detection_results.csv",
                mime="text/csv",
            )

            if "label" in df.columns:
                from sklearn.metrics import accuracy_score, precision_recall_fscore_support
                y_true = df["label"].astype(int)
                y_pred = out_df["pred_label"].astype(int)
                p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
                st.write({
                    "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
                    "precision": round(float(p), 4),
                    "recall": round(float(r), 4),
                    "f1": round(float(f1), 4),
                })

with tab_compare:
    st.subheader("模块分数对比")
    compare_text = st.text_area("输入用于对比的文本", value="加 v 信 领·取 优 惠，先到先得", height=100)
    if st.button("生成对比"):
        out = make_prediction(compare_text, threshold, model_mode, transformer_dir)
        chart_df = pd.DataFrame([
            {"module": "Rule", "score": out["rule_score"]},
            {"module": "Variant", "score": out["variant_score"]},
            {"module": "TF-IDF/LR", "score": out["tfidf_score"] or 0.0},
            {"module": "Transformer", "score": out["transformer_score"] or 0.0},
            {"module": "Final", "score": out["risk_score"]},
        ])
        st.bar_chart(chart_df, x="module", y="score")
        st.json(out)

with tab_train:
    st.subheader("BERT/RoBERTa 微调方式")
    st.markdown("""
本高级版已经加入可选 Transformer 支持。由于预训练模型体积较大，压缩包中没有内置权重。联网或已有本地 HuggingFace 缓存时，可运行：

```bash
pip install torch transformers accelerate datasets
python -m spam_detector.train_transformer \\
  --data data/sample_comments.csv \\
  --model_name_or_path hfl/chinese-roberta-wwm-ext \\
  --output_dir models/roberta_spam \\
  --epochs 3 \\
  --batch_size 16
```

如果服务器不能联网，可以先手动下载模型，然后把 `--model_name_or_path` 改成本地路径。训练完成后，在左侧把 checkpoint 目录设置为 `models/roberta_spam`，Demo 会自动调用 RoBERTa 模型。
""")
