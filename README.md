# 基于字符相似性与机器学习的互联网垃圾文本检测系统

本项目是“文本检测：互联网大数据实践”方向的课程大作业完整实现包，主题为：

> **面向社交平台评论的变体垃圾广告文本检测实践**

项目包含数据构造、文本预处理、规则检测、字符相似性变体归一化、机器学习分类、融合打分、实验评估、Web Demo 和报告材料。

## 1. 项目亮点

- **任务完整**：完成正常/垃圾文本二分类，并输出风险分数和命中原因。
- **可解释**：规则模块能解释 URL、手机号、微信引流、返现优惠、进群扫码等风险。
- **针对变体垃圾文本**：加入字形相似、字音近似、拼音缩写、分隔符插入等归一化策略。
- **降低误报**：识别技术讨论、课程实验、反诈分析等正常语境，减少单纯关键词命中导致的误判。
- **风险分层**：输出垃圾类型和处置建议，支持正常通过、人工复核、拦截三类结果。
- **可复现实验**：提供数据生成、训练、评估脚本。
- **可展示系统**：提供 Streamlit 交互式 Web Demo。
- **便于扩展**：可将 `data/sample_comments.csv` 替换为真实标注数据后重新训练。

## 2. 文件结构

```text
spam_text_detection_project/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── sample_comments.csv
│   └── challenging_cases.csv
├── models/
│   └── tfidf_lr.joblib
├── spam_detector/
├── reports/
├── figures/
└── tests/
```

## 3. 快速运行

安装依赖：

```bash
pip install -r requirements.txt
```

生成示例数据：

```bash
python -m spam_detector.make_dataset
```

训练模型：

```bash
python -m spam_detector.train --data data/sample_comments.csv
```

单条预测：

```bash
python -m spam_detector.predict --text "加薇信免费领取资料"
```

启动 Web Demo：

```bash
streamlit run app.py
```

## 4. 替换真实数据

真实数据只需要准备 CSV：

```csv
text,label
这个课程讲得很清楚,0
加微信领取优惠券,1
```

其中 `label=0` 表示正常文本，`label=1` 表示垃圾文本。然后运行：

```bash
python -m spam_detector.train --data data/your_dataset.csv --model models/tfidf_lr.joblib
python -m spam_detector.evaluate --data data/your_dataset.csv --model models/tfidf_lr.joblib
```

## 5. 小组分工建议

- 成员 A：数据收集、清洗、标注规范、数据分析。
- 成员 B：规则检测、传统机器学习 baseline、评估指标。
- 成员 C：字符相似性模块、变体增强、模型训练。
- 成员 D：系统 Demo、实验可视化、报告和答辩材料整合。

## 6. 注意

当前包内数据是为课程演示生成的示例数据，报告中已经明确说明。正式提交前建议补充真实评论或短信数据，使实验结果更有说服力。


## 7. BERT / RoBERTa 高级版

本版本新增可选的 BERT/RoBERTa 微调模块与高级 Demo。

训练中文 RoBERTa：

```bash
pip install torch transformers accelerate datasets
python -m spam_detector.train_transformer \
  --data data/sample_comments.csv \
  --model_name_or_path hfl/chinese-roberta-wwm-ext \
  --output_dir models/roberta_spam
```

启动高级 Demo：

```bash
streamlit run app_advanced.py
```

高级 Demo 支持：

- TF-IDF/LR 与 Transformer/RoBERTa 模式切换；
- 单条检测；
- 批量 CSV 检测；
- 检测结果下载；
- 关键词高亮；
- 垃圾类型识别与人工复核建议；
- 技术/学习/反诈正常语境下的误报缓解；
- 模块分数对比；
- RoBERTa checkpoint 自动加载与失败回退。

说明：预训练模型权重体积较大，压缩包不直接内置 RoBERTa 权重；联网或已有本地模型缓存时可直接训练。
