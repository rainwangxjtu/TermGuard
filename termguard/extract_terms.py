import re
from typing import List, Tuple
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

_EN_WORD = re.compile(r"[a-zA-Z][a-zA-Z0-9\-']*")


STOPWORDS = {
    "the","a","an","and","or","to","of","in","on","for","with","as","at","by",
    "is","are","was","were","be","been","being","it","this","that","these","those",
    "from","into","over","after","before","about","we","you","they","i","he","she",
    "them","his","her","our","their","your"
}


def _tokenize_en(s: str) -> List[str]:
    toks = [t.lower() for t in _EN_WORD.findall(s)]
    toks = [t for t in toks if t not in STOPWORDS]
    return toks


def extract_en_terms(sentences: List[str], top_k: int = 30, ngram_min: int = 1, ngram_max: int = 3,
                     min_chars: int = 3) -> List[Tuple[str, float]]:
    """
    Extract term candidates using TF-IDF over sentence corpus (word n-grams).
    Returns: list of (term, score) sorted desc.
    """
    if not sentences:
        return []

    # Prepare corpus
    corpus = [" ".join(_tokenize_en(s)) for s in sentences]
    corpus = [c for c in corpus if c.strip()]
    if not corpus:
        return []

    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(ngram_min, ngram_max),
        token_pattern=r"(?u)\b\w+\b",
        lowercase=True,
        min_df=1
    )
    X = vectorizer.fit_transform(corpus)  # (n_sent, n_terms)
    terms = np.array(vectorizer.get_feature_names_out())

    # Score terms by total TF-IDF across sentences
    scores = np.asarray(X.sum(axis=0)).ravel()
    # Filter short / low-information ngrams
    good = []
    for t, sc in zip(terms, scores):
        if len(t) < min_chars:
            continue
        # remove ngrams that are mostly stopwords
        parts = t.split()
        if all(p in STOPWORDS for p in parts):
            continue
        good.append((t, float(sc)))

    good.sort(key=lambda x: x[1], reverse=True)

    # Also encourage terms that appear multiple times
    counts = Counter(" ".join(corpus).split())
    boosted = []
    for t, sc in good:
        freq_boost = 1.0
        # boost unigram frequency lightly
        if " " not in t:
            freq_boost += min(1.5, 0.1 * counts[t])
        boosted.append((t, sc * freq_boost))

    boosted.sort(key=lambda x: x[1], reverse=True)
    return boosted[:top_k]
