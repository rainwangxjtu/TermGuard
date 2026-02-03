from collections import Counter
from typing import Dict, List, Tuple, Optional

import jieba

from .utils import contains_en_term


def zh_tokenize(s: str) -> List[str]:
    return [t.strip() for t in jieba.lcut(s) if t.strip()]


def zh_ngrams(tokens: List[str], max_n: int = 4) -> List[str]:
    grams: List[str] = []
    n = len(tokens)
    for k in range(1, max_n + 1):
        for i in range(0, n - k + 1):
            g = "".join(tokens[i:i + k])
            if g.strip():
                grams.append(g)
    return grams


def align_terms(
    aligned_pairs: List[Tuple[str, str]],
    en_terms: List[str],
    zh_ngram_max: int = 4,
    max_candidates: int = 5,
    glossary: Optional[Dict[str, str]] = None,
) -> Dict[str, List[Tuple[str, float, int]]]:
    glossary = glossary or {}
    en_lower = [en.lower() for en, _ in aligned_pairs]
    results: Dict[str, List[Tuple[str, float, int]]] = {}

    for term in en_terms:
        extra_variants: List[str] = []

        term_lower = term.lower()
        idxs = [i for i, s in enumerate(en_lower) if contains_en_term(s, term_lower)]
        if not idxs:
            results[term] = []
            continue

        counts: Counter = Counter()
        total_pairs = 0

        for i in idxs:
            _, zh = aligned_pairs[i]
            toks = zh_tokenize(zh)
            grams = zh_ngrams(toks, max_n=zh_ngram_max)

            for g in grams:
                if len(g) < 2:
                    continue
                if any(ch in g for ch in ["的", "了", "在", "是", "和", "与"]):
                    continue
                counts[g] += 1

            total_pairs += 1

        scored: List[Tuple[str, float, int]] = []
        for zh_term, c in counts.items():
            if c < 2:
                continue
            score = c / max(1, total_pairs)
            scored.append((zh_term, float(score), int(c)))
        scored.sort(key=lambda x: (x[2], x[1]), reverse=True)

        if term in glossary:
            pref = glossary[term]

            if pref.endswith("项目") and "无人机" in pref:
                extra_variants.append(pref.replace("无人机", "无人飞行器"))

            zh_concat = " ".join([aligned_pairs[i][1] for i in idxs])
            for v in extra_variants:
                if v in zh_concat:
                    counts[v] += 2  # boost

            rescored: List[Tuple[str, float, int]] = []
            for zh_term, c in counts.items():
                if c < 2:
                    continue
                score = c / max(1, total_pairs)
                rescored.append((zh_term, float(score), int(c)))
            rescored.sort(key=lambda x: (x[2], x[1]), reverse=True)

            pref_count = counts.get(pref, 0)
            anchored = [(pref, 999.0, int(pref_count) + 1)]
            alternates = [(z, s, ct) for (z, s, ct) in rescored if z != pref]
            results[term] = anchored + alternates[: max(0, max_candidates - 1)]
        else:
            results[term] = scored[:max_candidates]

    return results
