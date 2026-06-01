import json
from pathlib import Path
import streamlit as st

from spam_detector.ensemble import explain_prediction
from spam_detector.model import load_model

st.set_page_config(page_title="互联网垃圾文本检测系统", page_icon="🛡️", layout="wide")

st.title("🛡️ 互联网垃圾文本检测系统")
st.caption("规则检测 + 字符相似性变体归一化 + TF-IDF/Logistic Regression 融合打分")

MODEL_PATH = Path("models/tfidf_lr.joblib")
model = load_model(MODEL_PATH) if MODEL_PATH.exists() else None

examples = [
    "这个课程讲得挺清楚的，案例也很实用。",
    "加薇信免费领取资料，数量有限！",
    "私 聊 我 返·现，扫码进群领红包",
    "项目报告今天需要补充实验结果分析。",
    "点击www.example.com领取优惠券，加vx了解",
]

text = st.text_area("请输入待检测文本", value=examples[1], height=120)
threshold = st.slider("风险阈值", 0.0, 1.0, 0.50, 0.01)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("开始检测", type="primary"):
        result = explain_prediction(text, model=model, threshold=threshold)
        st.session_state["last_result"] = result

with col2:
    sample = st.selectbox("示例文本", examples)
    if st.button("使用示例"):
        st.session_state["last_result"] = explain_prediction(sample, model=model, threshold=threshold)

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    st.subheader("检测结果")
    if result["label"] == 1:
        st.error(f"{result['label_name']}，风险分数：{result['risk_score']:.3f}")
    else:
        st.success(f"{result['label_name']}，风险分数：{result['risk_score']:.3f}")
    st.write(f"处置建议：{result['review_status']}")
    if result["risk_categories"] and result["review_status"] != "通过":
        st.write("风险类型：" + "、".join(result["risk_categories"]))

    c1, c2, c3 = st.columns(3)
    c1.metric("规则分数", result["rule_score"])
    c2.metric("模型分数", "未加载" if result["model_score"] is None else result["model_score"])
    c3.metric("变体分数", result["variant_score"])

    st.markdown("**变体归一化文本：**")
    st.code(result["normalized_text"], language="text")

    st.markdown("**命中原因：**")
    for reason in result["reasons"]:
        st.write("- " + reason)

    with st.expander("查看 JSON 结果"):
        st.json(result)
else:
    st.info("输入文本后点击“开始检测”。")

st.divider()
st.markdown("""
### 系统说明
本 Demo 用于课程作业展示。实际提交时建议用真实标注数据重新训练模型，并补充误差分析。

运行方式：

```bash
python -m spam_detector.make_dataset
python -m spam_detector.train --data data/sample_comments.csv
streamlit run app.py
```
""")
