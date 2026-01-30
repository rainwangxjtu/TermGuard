# TermGuard — Terminology Consistency Checker (EN→ZH)

**TermGuard** is a modular **NLP + IR-style pipeline** that detects *terminology inconsistency* in bilingual translation data (English → Chinese), generates a structured **consistency report**, and optionally produces a **patched Chinese translation** that enforces a preferred glossary.

This project highlights:
- **Pipeline architecture** and replaceable modules (preprocess → extract → align → score → patch → report)
- **Algorithmic term extraction + alignment** (n-grams, TF-IDF weighting, co-occurrence mapping)
- **Quantitative signals** (entropy / probability-based severity scoring)
- **Reproducible experiments** via a command-line interface and deterministic demo inputs/outputs

---

## What it does

### Inputs
- **English source** text (`--en`)
- **Chinese translation** text (`--zh`)
- Optional **glossary CSV** (`--glossary`) mapping: `en_term,preferred_zh`

### Outputs
- `report.csv` / `report.json`: flagged terms, candidate translations, and severity metrics
- `zh_patched.txt`: Chinese translation normalized to the preferred glossary (optional)

---

## System Overview

Pipeline stages:
1) **Preprocess**: sentence segmentation + normalization  
2) **Term Extraction (EN)**: n-gram candidates + TF-IDF filtering  
3) **Alignment / Mapping (EN→ZH)**: sentence-pair co-occurrence + candidate scoring  
4) **Consistency Detection**: 1→many and many→1 mappings + **entropy-based severity**  
5) **Optional Patching**: replace inconsistent candidates with `preferred_zh` safely  
6) **Reporting**: export CSV/JSON artifacts for inspection and evaluation

---

## Quickstart (CLI)

### 1) Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Run the demo
```bash
rm -rf outputs/demo_final3

PYTHONPATH=. python ./cli.py \
  --en data/demo_en.txt \
  --zh data/demo_zh.txt \
  --glossary data/demo_glossary.csv \
  --out outputs/demo_final3
```
### 3) Inspect outputs
```bash
cat outputs/demo_final3/report.csv
echo "---- PATCHED ----"
cat outputs/demo_final3/zh_patched.txt
```
---
### Example Output (Demo)
The demo intentionally includes an inconsistent translation of “drone program” (e.g., 无人飞行器项目 vs 无人机项目).
TermGuard flags it in report.csv and produces a patched translation enforcing the preferred glossary term (无人机项目) in zh_patched.txt.
