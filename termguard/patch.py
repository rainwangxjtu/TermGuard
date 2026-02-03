# termguard/patch.py
import re
from typing import Dict, List


def _parse_candidate_zh_terms(s: str) -> List[str]:
    """
    Parse strings like: '无人机项目(2); 无人飞行器项目(3); 项目(2)'
    -> ['无人机项目', '无人飞行器项目', '项目']
    """
    parts = []
    for chunk in s.split(";"):
        c = chunk.strip()
        if not c:
            continue
        # remove trailing "(num)" if present
        c = re.sub(r"\(\d+\)\s*$", "", c).strip()
        if c:
            parts.append(c)
    return parts


def patch_zh_text(zh_text: str, glossary: Dict[str, str], flags: List[Dict]) -> str:
    patched = zh_text

    for f in flags:
        preferred = (f.get("preferred_zh") or "").strip()
        if not preferred:
            continue

        variants: List[str] = []

        # Case A: already structured
        if isinstance(f.get("candidate_terms"), list):
            variants.extend([str(x).strip() for x in f["candidate_terms"] if str(x).strip()])

        # Case B: stored as a single string like "xxx(2); yyy(3)"
        if isinstance(f.get("candidate_zh_terms"), str):
            variants.extend(_parse_candidate_zh_terms(f["candidate_zh_terms"]))

        # de-dup + replace longer first
        variants = sorted(set([v for v in variants if v]), key=len, reverse=True)

        for v in variants:
            if v == preferred:
                continue

            # Safety: avoid "无人机项目项目"
            if v in preferred:
                continue

            patched = re.sub(re.escape(v), preferred, patched)

        # collapse accidental duplicates
        dup = preferred + preferred
        while dup in patched:
            patched = patched.replace(dup, preferred)

    return patched
