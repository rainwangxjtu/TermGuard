import re
from typing import List, Tuple
from .utils import normalize_whitespace


_EN_SPLIT = re.compile(r"(?<=[\.\?\!])\s+")
_ZH_SPLIT = re.compile(r"(?<=[。！？])")


def split_en_sentences(text: str) -> List[str]:
    text = normalize_whitespace(text)
    if not text:
        return []
    # If file has multiple lines, keep them; also split long lines into sentences
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    sents: List[str] = []
    for ln in lines:
        parts = _EN_SPLIT.split(ln)
        sents.extend([p.strip() for p in parts if p.strip()])
    return sents


def split_zh_sentences(text: str) -> List[str]:
    text = normalize_whitespace(text)
    if not text:
        return []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    sents: List[str] = []
    for ln in lines:
        parts = [p.strip() for p in _ZH_SPLIT.split(ln) if p.strip()]
        # add punctuation back if lost
        rebuilt: List[str] = []
        buf = ""
        for ch in ln:
            buf += ch
            if ch in "。！？":
                rebuilt.append(buf.strip())
                buf = ""
        if buf.strip():
            rebuilt.append(buf.strip())
        sents.extend(rebuilt if rebuilt else parts)
    return sents


def align_sentence_pairs(en_text: str, zh_text: str) -> List[Tuple[str, str]]:
    """
    MVP alignment: split EN/ZH into sentences and align by index (truncate to min length).
    """
    en_sents = split_en_sentences(en_text)
    zh_sents = split_zh_sentences(zh_text)
    n = min(len(en_sents), len(zh_sents))
    return list(zip(en_sents[:n], zh_sents[:n]))
