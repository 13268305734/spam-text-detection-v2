import re
import unicodedata

_URL_RE = re.compile(r"(https?://|www\.|[a-zA-Z0-9.-]+\.(com|cn|net|org|top|xyz|vip|cc|io)\b)", re.I)
_PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d{9})(?!\d)")
_QQ_RE = re.compile(r"(?<!\d)[1-9]\d{5,11}(?!\d)")
_WS_RE = re.compile(r"\s+")
_HTML_RE = re.compile(r"<[^>]+>")

def to_half_width(text: str) -> str:
    """Normalize full-width forms to half-width forms with Unicode NFKC."""
    return unicodedata.normalize("NFKC", text or "")

def clean_text(text: str, keep_space: bool = False) -> str:
    """Basic cleaning for Chinese internet text.

    Steps:
    1. Unicode NFKC normalization, lower-casing for Latin characters.
    2. Replace URLs/phone-like numbers/QQ-like numbers with markers.
    3. Remove HTML tags and collapse whitespace.
    4. Keep Chinese, letters, digits, selected markers, and common punctuation.

    The function deliberately does not do word segmentation; most models in this
    project use char-level n-grams because spam variants often occur inside words.
    """
    text = to_half_width(text).lower()
    text = _HTML_RE.sub(" ", text)
    text = _URL_RE.sub(" <URL> ", text)
    text = _PHONE_RE.sub(" <PHONE> ", text)
    text = _QQ_RE.sub(" <NUMID> ", text)
    if keep_space:
        text = _WS_RE.sub(" ", text).strip()
    else:
        text = _WS_RE.sub("", text)
    return text

def char_tokens(text: str) -> str:
    """Return a space-separated char-token string for vectorizers."""
    text = clean_text(text)
    return " ".join(list(text))

def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))

def repeated_char_ratio(text: str) -> float:
    text = clean_text(text, keep_space=False)
    if not text:
        return 0.0
    repeats = sum(1 for i in range(1, len(text)) if text[i] == text[i-1])
    return repeats / max(len(text) - 1, 1)

def symbol_ratio(text: str) -> float:
    text = to_half_width(text)
    if not text:
        return 0.0
    symbol_count = sum(1 for ch in text if not (ch.isalnum() or "\u4e00" <= ch <= "\u9fff" or ch.isspace()))
    return symbol_count / len(text)
