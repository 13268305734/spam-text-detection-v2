from __future__ import annotations

import re
from typing import Dict, Iterable, List

from .similarity import normalize_variants, suspicious_keywords

REVIEW_LOW = 0.20

NORMAL_CONTEXT_RE = re.compile(
    r"(小程序|支付接口|开发|配置|环境|课程|作业|实验|论文|报告|案例|识别|检测|分析|讨论|反诈|防骗|风险提示)"
)
RISK_TERM_RE = re.compile(
    r"(微信|薇信|vx|wx|刷单|博彩|贷款|返现|红包|优惠|扫码|进群|私聊|链接|广告|诈骗)",
    re.I,
)

CATEGORY_BY_FEATURE = {
    "rule_wechat": "联系方式引流",
    "rule_phone": "联系方式引流",
    "rule_money": "优惠返现",
    "rule_group": "群聊导流",
    "rule_fraud": "诈骗/灰产推广",
    "rule_url": "链接推广",
}

CATEGORY_BY_KEYWORD = {
    "加微信": "联系方式引流",
    "微信": "联系方式引流",
    "私聊": "联系方式引流",
    "客服": "联系方式引流",
    "返现": "优惠返现",
    "红包": "优惠返现",
    "优惠": "优惠返现",
    "优惠券": "优惠返现",
    "免费领取": "优惠返现",
    "扫码": "群聊导流",
    "进群": "群聊导流",
    "拉群": "群聊导流",
    "刷单": "诈骗/灰产推广",
    "博彩": "诈骗/灰产推广",
    "贷款": "诈骗/灰产推广",
    "兼职": "诈骗/灰产推广",
    "点击链接": "链接推广",
    "推广": "链接推广",
    "引流": "链接推广",
}


def has_normal_context(text: str) -> bool:
    searchable = f"{text or ''} {normalize_variants(text or '')}"
    return bool(RISK_TERM_RE.search(searchable) and NORMAL_CONTEXT_RE.search(searchable))


def apply_context_suppression(score: float, text: str) -> tuple[float, list[str]]:
    if not has_normal_context(text):
        return score, []
    return min(score * 0.35, score), ["检测到技术/学习/反诈等正常语境，降低关键词误报风险"]


def infer_risk_categories(features: Dict[str, int], keywords: Iterable[str]) -> List[str]:
    categories: List[str] = []
    for feature, category in CATEGORY_BY_FEATURE.items():
        if features.get(feature):
            categories.append(category)
    for keyword in keywords:
        category = CATEGORY_BY_KEYWORD.get(keyword)
        if category:
            categories.append(category)
    return list(dict.fromkeys(categories))


def review_status(score: float, threshold: float, categories: Iterable[str]) -> str:
    if score >= threshold:
        return "拦截"
    if score >= REVIEW_LOW and list(categories):
        return "建议人工复核"
    return "通过"


def risk_keywords(text: str) -> List[str]:
    return suspicious_keywords(text)
