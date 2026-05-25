from __future__ import annotations
import re
from typing import Dict, List, Tuple
from .preprocess import repeated_char_ratio, symbol_ratio
from .similarity import suspicious_keywords, normalize_variants

URL_RE = re.compile(r"(https?://|www\.|\.com|\.cn|\.net|\.top|\.xyz)", re.I)
PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
WECHAT_RE = re.compile(r"(vx|wx|v信|微信|薇信|加v|加微|加薇)", re.I)
MONEY_RE = re.compile(r"(返现|红包|赚钱|到账|佣金|优惠券|免费领取|限时|秒杀)")
GROUP_RE = re.compile(r"(进群|拉群|群号|扫码|二维码)")
FRAUD_RE = re.compile(r"(刷单|博彩|贷款|裸聊|代开|套现)")

RULES = [
    ("url", URL_RE, 0.18, "包含链接或疑似域名"),
    ("phone", PHONE_RE, 0.20, "包含手机号"),
    ("wechat", WECHAT_RE, 0.22, "包含微信/联系方式引流词"),
    ("money", MONEY_RE, 0.15, "包含返现/优惠/收益诱导词"),
    ("group", GROUP_RE, 0.12, "包含进群/扫码等导流词"),
    ("fraud", FRAUD_RE, 0.25, "包含高风险词"),
]

def rule_score(text: str) -> Tuple[float, List[str], Dict[str, int]]:
    """Interpretable rule-based risk score."""
    raw = text or ""
    normalized = normalize_variants(raw)
    searchable = raw + " " + normalized
    score = 0.0
    reasons: List[str] = []
    features: Dict[str, int] = {}

    for name, regex, weight, reason in RULES:
        hit = 1 if regex.search(searchable) else 0
        features[f"rule_{name}"] = hit
        if hit:
            score += weight
            reasons.append(reason)

    hits = suspicious_keywords(raw)
    features["keyword_count"] = len(hits)
    if hits:
        score += min(0.05 * len(hits), 0.18)
        reasons.append("命中垃圾文本关键词：" + "、".join(hits[:5]))

    rep = repeated_char_ratio(raw)
    sym = symbol_ratio(raw)
    features["high_repeat"] = int(rep > 0.20)
    features["high_symbol"] = int(sym > 0.25)

    if rep > 0.20:
        score += 0.08
        reasons.append("重复字符比例偏高")
    if sym > 0.25:
        score += 0.08
        reasons.append("特殊符号比例偏高")

    return min(score, 1.0), reasons, features
