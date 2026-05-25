# V2 升级记录

## 新增能力

1. 新增 `spam_detector/bert_model.py`
   - 支持 HuggingFace BERT/RoBERTa 微调；
   - 支持 checkpoint 加载；
   - 支持输出垃圾文本概率。

2. 新增 `spam_detector/train_transformer.py`
   - 可通过命令行训练 `bert-base-chinese`、`hfl/chinese-roberta-wwm-ext`、`hfl/chinese-macbert-base` 等模型。

3. 新增 `app_advanced.py`
   - 单条检测；
   - 批量 CSV 检测；
   - 关键词高亮；
   - 风险分数进度条；
   - 模块分数对比图；
   - TF-IDF 与 Transformer 模式切换；
   - Transformer checkpoint 不存在时自动回退。

4. 新增报告说明
   - `reports/BERT_RoBERTa升级说明.md`。

## 注意

压缩包没有内置大型预训练模型权重。需要联网或本地 HuggingFace 缓存才能训练 RoBERTa。基础 TF-IDF/LR 模型和高级 Demo 的回退模式可以直接运行。
