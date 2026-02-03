import re
from dataclasses import dataclass
from time import perf_counter
from pathlib import Path


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str, content: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


def safe_mkdir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def normalize_whitespace(s: str) -> str:
    s = s.replace("\u3000", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s+\n", "\n", s)
    return s.strip()


@dataclass
class Timer:
    start: float = 0.0

    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = perf_counter() - self.start  # type: ignore[attr-defined]


def contains_en_term(sentence_lower: str, term_lower: str) -> bool:
    # boundary-safe for alphabetic terms; fallback to substring
    if re.fullmatch(r"[a-z0-9 ]+", term_lower):
        pat = r"\b" + re.escape(term_lower) + r"\b"
        return re.search(pat, sentence_lower) is not None
    return term_lower in sentence_lower
