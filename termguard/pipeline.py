from __future__ import annotations
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd

from .config import TermGuardConfig
from .logger import get_logger
from .utils import read_text, write_text, safe_mkdir, Timer
from .preprocess import align_sentence_pairs
from .extract_terms import extract_en_terms
from .align import align_terms
from .consistency import detect_inconsistencies
from .patch import patch_zh_text
from .report import write_report

def load_glossary_csv(path: str) -> dict[str, str]:
    import pandas as pd

    df = pd.read_csv(path)

    # normalize headers: strip whitespace + BOM
    df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]

    # accept multiple header conventions
    en_col = "en_term" if "en_term" in df.columns else ("en" if "en" in df.columns else "term")
    zh_col = "zh_term" if "zh_term" in df.columns else ("preferred_zh" if "preferred_zh" in df.columns else "zh")

    glossary = {}
    for _, r in df.iterrows():
        en = str(r[en_col]).strip()
        zh = str(r[zh_col]).strip()
        if en and zh:
            glossary[en] = zh
    return glossary

def run_pipeline(
    en_text: str,
    zh_text: str,
    glossary: Optional[Dict[str, str]] = None,
    out_dir: str = "outputs/run",
    config: Optional[TermGuardConfig] = None,
    log_path: Optional[str] = None
) -> Dict[str, Any]:
    cfg = config or TermGuardConfig()
    safe_mkdir(out_dir)
    logger = get_logger(log_path=log_path or str(Path(out_dir) / "termguard.log"))

    glossary = glossary or {}

    stage_times: Dict[str, float] = {}

    # 1) align sentence pairs
    with Timer() as t:
        pairs = align_sentence_pairs(en_text, zh_text)
    stage_times["preprocess_align"] = t.elapsed
    logger.info(f"[preprocess] aligned_pairs={len(pairs)} time={t.elapsed:.3f}s")

    en_sents = [p[0] for p in pairs]

    # 2) extract EN terms
    with Timer() as t:
        term_scored = extract_en_terms(
            en_sents,
            top_k=cfg.top_k_terms,
            ngram_min=cfg.ngram_min,
            ngram_max=cfg.ngram_max,
            min_chars=cfg.min_term_chars
        )
        # ✅ For a clean terminology QA demo: prioritize glossary terms
        if glossary:
            # Keep glossary terms that actually appear in the English text (case-insensitive)
            en_text_lower = en_text.lower()
            en_terms = [t for t in glossary.keys() if " " in t and t.lower() in en_text_lower]
        else:
            en_terms = [tup[0] for tup in term_scored]

    stage_times["extract_terms"] = t.elapsed
    logger.info(f"[terms] extracted_terms={len(en_terms)} time={t.elapsed:.3f}s")

    # 3) align terms EN->ZH
    with Timer() as t:
        mappings = align_terms(
            aligned_pairs=pairs,
            en_terms=en_terms,
            zh_ngram_max=cfg.zh_ngram_max,
            max_candidates=cfg.max_zh_candidates_per_en_term,
            glossary=glossary
        )
    stage_times["align_terms"] = t.elapsed
    logger.info(f"[align] mapped_terms={len(mappings)} time={t.elapsed:.3f}s")

    # 4) detect inconsistencies
    with Timer() as t:
        flags = detect_inconsistencies(
            mappings=mappings,
            glossary=glossary,
            min_total_occurrences=cfg.min_total_occurrences,
            entropy_threshold=cfg.flag_entropy_threshold
        )
    stage_times["detect_inconsistencies"] = t.elapsed
    logger.info(f"[consistency] flags={len(flags)} time={t.elapsed:.3f}s")

    # 5) patch zh text (optional)
    patched_zh = zh_text
    with Timer() as t:
        if cfg.enable_patching and glossary:
            patched_zh = patch_zh_text(zh_text, glossary, flags)
    stage_times["patch"] = t.elapsed
    logger.info(f"[patch] enabled={cfg.enable_patching and bool(glossary)} time={t.elapsed:.3f}s")

    # 6) write outputs
    with Timer() as t:
        csv_path, json_path = write_report(out_dir, flags)
        patched_path = str(Path(out_dir) / "zh_patched.txt")
        write_text(patched_path, patched_zh)
        # also save top terms for transparency
        terms_path = str(Path(out_dir) / "extracted_terms.txt")
        write_text(terms_path, "\n".join([f"{term}\t{score:.4f}" for term, score in term_scored]))
    stage_times["write_outputs"] = t.elapsed

    logger.info(f"[output] report_csv={csv_path}")
    logger.info(f"[output] report_json={json_path}")
    logger.info(f"[output] zh_patched={patched_path}")

    return {
        "aligned_pairs": len(pairs),
        "extracted_terms": term_scored,
        "mappings": mappings,
        "flags": flags,
        "report_csv": csv_path,
        "report_json": json_path,
        "patched_path": patched_path,
        "stage_times": stage_times,
    }


def run_pipeline_from_files(
    en_path: str,
    zh_path: str,
    glossary_path: str | None,
    out_dir: str,
    config: TermGuardConfig | None = None
) -> Dict[str, Any]:
    en_text = read_text(en_path)
    zh_text = read_text(zh_path)
    glossary = load_glossary_csv(glossary_path) if glossary_path else {}
    return run_pipeline(
        en_text=en_text,
        zh_text=zh_text,
        glossary=glossary,
        out_dir=out_dir,
        config=config
    )
