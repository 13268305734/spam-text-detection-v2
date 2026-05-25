from __future__ import annotations
import re
from typing import Dict, List, Tuple

# Character-level variant map. In a real production system this can be expanded
# using a pinyin dictionary, OCR confusable table, and historical adversarial samples.
CONFUSABLE_MAP: Dict[str, str] = {
    # 微信
    "薇": "微", "徽": "微", "威": "微", "危": "微", "v": "微", "V": "微",
    "辛": "信", "芯": "信", "心": "信", "訫": "信",
    # 加、联系、领取、优惠、链接
    "+": "加", "➕": "加", "佳": "加", "珈": "加",
    "莲": "联", "连": "联", "链": "联",
    "繫": "系", "係": "系",
    "令": "领", "零": "领",
    "娶": "取",
    "幽": "优", "忧": "优",
    "慧": "惠", "会": "惠",
    "姐": "接",
    # Common Latin shorthand
    "ｗ": "w", "ｖ": "v", "ｘ": "x",
}

PHRASE_MAP: Dict[str, str] = {
    "wx": "微信",
    "vx": "微信",
    "v信": "微信",
    "微x": "微信",
    "微 信": "微信",
    "w x": "微信",
    "v x": "微信",
    "加微": "加微信",
    "加v": "加微信",
    "加vx": "加微信",
    "加wx": "加微信",
    "私聊": "私聊",
}

SPAM_KEYWORDS = [
    "加微信", "微信", "私聊", "返现", "优惠", "优惠券", "代理", "兼职",
    "刷单", "薅羊毛", "免费领取", "点击链接", "博彩", "贷款", "秒到账",
    "扫码", "进群", "拉群", "引流", "推广", "微商", "客服", "红包",
]

def remove_separators(text: str) -> str:
    return re.sub(r"[\s·•,，.。!！?？:：;；_—~～|/\\\-]+", "", text or "")

def normalize_variants(text: str) -> str:
    """Map suspicious confusable characters/phrases to canonical forms."""
    if not text:
        return ""
    compact = remove_separators(str(text))
    # Phrase-level canonicalization first.
    for src, dst in sorted(PHRASE_MAP.items(), key=lambda kv: -len(kv[0])):
        if src != dst:
            compact = compact.replace(src, dst)
    compact = compact.replace("加微信信", "加微信").replace("微信信", "微信")
    chars = [CONFUSABLE_MAP.get(ch, ch) for ch in compact]
    normalized = "".join(chars)
    for src, dst in sorted(PHRASE_MAP.items(), key=lambda kv: -len(kv[0])):
        if src != dst:
            normalized = normalized.replace(src, dst)
    # Fix potential overlapping replacement artifacts
    normalized = normalized.replace("加微信信", "加微信").replace("微信信", "微信")
    return normalized

def suspicious_keywords(text: str) -> List[str]:
    normalized = normalize_variants(text)
    hits = []
    for kw in SPAM_KEYWORDS:
        if kw in normalized:
            hits.append(kw)
    return sorted(set(hits), key=lambda x: SPAM_KEYWORDS.index(x))

def variant_score(text: str) -> Tuple[float, List[str]]:
    """Return a simple variant-based risk score and explanations."""
    raw = text or ""
    compact = remove_separators(raw)
    normalized = normalize_variants(raw)
    hits = suspicious_keywords(raw)
    reasons = []
    score = 0.0

    if hits:
        score += min(0.15 * len(hits), 0.55)
        reasons.append("变体归一化后命中关键词：" + "、".join(hits[:5]))

    if normalized != compact and hits:
        score += 0.25
        reasons.append("发现疑似同音/形近/拼音缩写规避写法")

    separators = len(re.findall(r"[\s·•_—~～|/\\\-]+", raw))
    if separators >= 2 and len(compact) <= 30:
        score += 0.15
        reasons.append("短文本中插入了较多分隔符")

    return min(score, 1.0), reasons

def augment_variant(text: str) -> str:
    """Generate one obfuscated variant for data augmentation."""
    replacements = {
        "微信": "薇信",
        "加微信": "加v信",
        "免费": "免 费",
        "领取": "领·取",
        "优惠": "优 惠",
        "链接": "链 接",
        "私聊": "私 聊",
        "返现": "返·现",
    }
    out = text
    for src, dst in replacements.items():
        out = out.replace(src, dst)
    return out
