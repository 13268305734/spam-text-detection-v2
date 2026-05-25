from __future__ import annotations
import random
from pathlib import Path
import pandas as pd
from .config import RANDOM_SEED
from .similarity import augment_variant

NORMAL_TEMPLATES = [
    "这个课程讲得很清楚，案例也比较实用。",
    "今天的天气很好，下午准备去图书馆学习。",
    "老师布置的实验需要先完成数据预处理。",
    "这家店的服务态度不错，物流速度也很快。",
    "我觉得这个算法还有优化空间，可以继续调参。",
    "论文主要介绍了文本分类模型和评测指标。",
    "项目进度正常，明天继续整理实验结果。",
    "这条评论只是普通交流，没有广告内容。",
    "请大家按时提交报告和代码说明。",
    "模型训练完成后需要保存参数并做测试。",
    "这个电影剧情一般，但演员表现还可以。",
    "我们小组今天讨论了系统架构和页面设计。",
    "数据标注规范需要统一，否则会影响实验结果。",
    "阅读材料里提到了召回率和精确率的区别。",
    "周末打算复习机器学习和自然语言处理。",
]

SPAM_TEMPLATES = [
    "加微信免费领取课程资料，数量有限。",
    "私聊我返现，扫码进群领红包。",
    "点击链接领取优惠券，限时秒杀。",
    "兼职刷单日结，佣金秒到账，加vx了解。",
    "贷款快速到账，无需抵押，微信联系。",
    "加微代理赚钱，团队扶持，轻松月入过万。",
    "进群领取福利，群内每天发红包。",
    "添加客服微信，免费领取内部资料。",
    "扫码加好友，优惠活动马上结束。",
    "低价推广引流，精准获客，联系wx。",
    "博彩平台开户，首充返利，私聊领取。",
    "加薇信领优惠，名额有限先到先得。",
    "V信联系，免费领取资料包。",
    "点击www.example.com领取福利。",
    "联系电话13800138000，优惠名额有限。",
]

NORMAL_EXTRA = [
    "系统设计", "实验分析", "数据清洗", "模型训练", "代码注释",
    "课程作业", "学习计划", "课堂讨论", "算法实现", "报告撰写",
]
SPAM_EXTRA = [
    "免费", "返现", "红包", "优惠", "代理", "加微信", "私聊", "扫码", "进群", "链接",
]

def synthesize(n_normal: int = 1200, n_spam: int = 1200, seed: int = RANDOM_SEED) -> pd.DataFrame:
    random.seed(seed)
    rows = []
    for _ in range(n_normal):
        base = random.choice(NORMAL_TEMPLATES)
        if random.random() < 0.35:
            base += " " + random.choice(NORMAL_EXTRA) + "部分还需要完善。"
        if random.random() < 0.10:
            base = base.replace("，", " ")
        rows.append({"text": base, "label": 0, "source": "synthetic_normal"})

    for _ in range(n_spam):
        base = random.choice(SPAM_TEMPLATES)
        if random.random() < 0.35:
            base += random.choice(SPAM_EXTRA)
        if random.random() < 0.45:
            base = augment_variant(base)
        if random.random() < 0.20:
            base = "🔥" + base + "！！！"
        rows.append({"text": base, "label": 1, "source": "synthetic_spam"})

    random.shuffle(rows)
    return pd.DataFrame(rows)

def main(out_path: str = "data/sample_comments.csv"):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df = synthesize()
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"saved {len(df)} rows to {out}")

if __name__ == "__main__":
    main()
