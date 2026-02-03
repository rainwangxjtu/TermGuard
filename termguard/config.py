from dataclasses import dataclass


@dataclass(frozen=True)
class TermGuardConfig:
    # Term extraction
    ngram_min: int = 1
    ngram_max: int = 3
    top_k_terms: int = 30
    min_term_chars: int = 3

    # Alignment
    zh_ngram_max: int = 4
    max_zh_candidates_per_en_term: int = 5

    # Consistency
    min_total_occurrences: int = 2
    flag_entropy_threshold: float = 0.65  # higher => more inconsistent

    # Patching
    enable_patching: bool = True
