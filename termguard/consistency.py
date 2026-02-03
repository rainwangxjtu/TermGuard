from __future__ import annotations
from typing import Dict, List, Tuple, Any
from collections import Counter
import math


def _entropy(probs: List[float]) -> float:
    e = 0.0
    for p in probs:
        if p > 0:
            e -= p * math.log(p + 1e-12)
    return e


def detect_inconsistencies(
    mappings: Dict[str, List[Tuple[str, float, int]]],
    glossary: Dict[str, str] | None = None,
    min_total_occurrences: int = 2,
    entropy_threshold: float = 0.65
) -> List[Dict[str, Any]]:
    """
    Identify EN terms with multiple plausible ZH variants.
    Uses candidate counts to compute entropy; flags if entropy above threshold.
    """
    glossary = glossary or {}
    flags: List[Dict[str, Any]] = []

    for en_term, candidates in mappings.items():
        if not candidates:
            continue

        counts = [c[2] for c in candidates]
        total = sum(counts)
        if total < min_total_occurrences:
            continue

        probs = [c / total for c in counts]
        ent = _entropy(probs)

        preferred = glossary.get(en_term, candidates[0][0])
        alternates = [c[0] for c in candidates if c[0] != preferred]

        # Severity heuristic: entropy + (1 - top_prob)
        top_prob = max(probs) if probs else 0.0
        severity = float(ent + (1.0 - top_prob))

        is_inconsistent = (len(candidates) >= 2 and ent >= entropy_threshold) or (preferred != candidates[0][0])

        if is_inconsistent:
            cands = mappings.get(en_term, [])
            candidate_terms = [t for (t, _, _) in cands]
            candidate_zh_terms = "; ".join([f"{t}({ct})" for (t, _, ct) in cands])

            flags.append({
                "en_term": en_term,
                "preferred_zh": preferred,
                "candidate_terms": candidate_terms,
                "candidate_zh_terms": candidate_zh_terms,
                "candidates": [
                    {"zh_term": z, "score": s, "count": ct} for (z, s, ct) in candidates
                ],
                "total_occurrences": total,
                "entropy": float(ent),
                "top_prob": float(top_prob),
                "severity": severity,
                "alternates": alternates
            })

    flags.sort(key=lambda x: x["severity"], reverse=True)
    return flags
