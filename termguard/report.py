from __future__ import annotations
from typing import Dict, List, Tuple, Any
from pathlib import Path
import json
import pandas as pd


def make_report_dataframe(flags: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for f in flags:
        cand_str = "; ".join([f"{c['zh_term']}({c['count']})" for c in f["candidates"]])
        rows.append({
            "en_term": f["en_term"],
            "preferred_zh": f["preferred_zh"],
            "candidate_zh_terms": cand_str,
            "total_occurrences": f["total_occurrences"],
            "entropy": f["entropy"],
            "top_prob": f["top_prob"],
            "severity": f["severity"],
        })
    df = pd.DataFrame(rows)
    return df


def write_report(out_dir: str, flags: List[Dict[str, Any]]) -> Tuple[str, str]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    df = make_report_dataframe(flags)

    csv_path = str(Path(out_dir) / "report.csv")
    json_path = str(Path(out_dir) / "report.json")

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    Path(json_path).write_text(json.dumps(flags, ensure_ascii=False, indent=2), encoding="utf-8")

    return csv_path, json_path
