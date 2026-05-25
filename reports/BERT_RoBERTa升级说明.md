# BERT / RoBERTa 升级说明

## 1. 升级内容

在原有版本“规则检测 + 字符相似性变体归一化 + TF-IDF/LR”的基础上，本版本加入了可选的 BERT/RoBERTa 深度学习模块和高级 Demo。

新增文件：

| 文件 | 说明 |
|---|---|
| `spam_detector/bert_model.py` | Transformer 数据集、训练、加载、预测函数 |
| `spam_detector/train_transformer.py` | BERT/RoBERTa 微调命令行脚本 |
| `app_advanced.py` | 高级 Streamlit Demo |
| `reports/BERT_RoBERTa升级说明.md` | 本说明文件 |

## 2. 为什么不直接把 RoBERTa 权重放进压缩包

常用中文预训练模型体积较大，例如 `bert-base-chinese`、`hfl/chinese-roberta-wwm-ext` 通常需要数百 MB。课程作业压缩包不适合直接内置这些权重，因此本项目采用“代码支持 + 本地训练/加载”的方式。

这也是更规范的工程做法：代码仓库保存训练逻辑和配置，模型权重通过训练产物或模型仓库管理。

## 3. 推荐模型

| 模型 | 说明 |
|---|---|
| `bert-base-chinese` | 基础中文 BERT，容易下载和复现 |
| `hfl/chinese-roberta-wwm-ext` | 中文 RoBERTa-wwm，通常比原始 BERT 更适合中文任务 |
| `hfl/chinese-macbert-base` | MacBERT，中文理解能力较强 |

## 4. 安装依赖

```bash
pip install torch transformers accelerate datasets
```

原项目基础依赖仍然需要：

```bash
pip install -r requirements.txt
```

## 5. 训练 RoBERTa

```bash
python -m spam_detector.train_transformer \
  --data data/sample_comments.csv \
  --model_name_or_path hfl/chinese-roberta-wwm-ext \
  --output_dir models/roberta_spam \
  --epochs 3 \
  --batch_size 16 \
  --learning_rate 2e-5
```

如果不能联网，需要先将模型下载到本地，然后运行：

```bash
python -m spam_detector.train_transformer \
  --data data/sample_comments.csv \
  --model_name_or_path /path/to/local/chinese-roberta-wwm-ext \
  --output_dir models/roberta_spam
```

## 6. 启动高级 Demo

```bash
streamlit run app_advanced.py
```

左侧可以选择：

1. `TF-IDF/LR`：使用轻量模型；
2. `Transformer/RoBERTa 优先`：优先使用 RoBERTa，若 checkpoint 不存在则回退；
3. `TF-IDF + Transformer 双模型`：两个模型概率取平均后再融合；
4. `仅规则+变体`：不依赖机器学习模型。

## 7. 高级 Demo 功能

相比基础 Demo，`app_advanced.py` 增加了：

- 单条检测；
- 批量 CSV 检测；
- 结果 CSV 下载；
- 模块风险分数对比图；
- 原文本关键词高亮；
- Transformer/RoBERTa checkpoint 配置；
- 自动回退机制；
- 训练命令展示。

## 8. 写进报告的建议

可以在报告“方法设计”部分加入：

> 为进一步提升语义理解能力，系统预留 BERT/RoBERTa 微调模块。该模块使用中文预训练语言模型对文本进行上下文编码，再通过分类头输出垃圾文本概率。与 TF-IDF 字符 n-gram 方法相比，BERT/RoBERTa 可以更好地区分“加微信领优惠”等真实垃圾文本和“微信小程序开发”等正常技术语境。考虑到预训练模型权重体积较大，项目压缩包不直接附带权重，而提供完整训练和加载脚本，支持在本地或服务器上复现。
