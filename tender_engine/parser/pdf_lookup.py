"""Searchable PDF lookup for tender source files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List

from .pdf_reader import read_pdf_pages

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "input"
CACHE_DIR = BASE_DIR / "cache" / "pdf_lookup"


@dataclass
class PDFSnippet:
    tender_id: str
    pdf_file: str
    page: int
    score: int
    snippet: str


def build_pdf_lookup(tender_id: str, force: bool = False) -> Path:
    """Extract text from all tender PDFs and cache it as JSON."""
    tender_id = str(tender_id).strip()
    tender_dir = INPUT_DIR / tender_id
    if not tender_dir.exists():
        raise FileNotFoundError(f"Tender input folder not found: {tender_dir}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / f"{tender_id}.json"
    if cache_path.exists() and not force:
        return cache_path

    rows = []
    for pdf in sorted(tender_dir.glob("*.pdf")):
        try:
            pages = read_pdf_pages(str(pdf))
        except Exception as exc:
            rows.append({"pdf_file": pdf.name, "page": 0, "text": "", "error": str(exc)})
            continue
        for idx, text in enumerate(pages, start=1):
            rows.append({"pdf_file": pdf.name, "page": idx, "text": _clean(text)})

    cache_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return cache_path


def lookup_pdf_text(tender_id: str, query: str, limit: int = 10) -> List[dict]:
    """Search cached tender PDFs and return best matching snippets."""
    tender_id = str(tender_id).strip()
    query = str(query or "").strip()
    if not query:
        return []

    cache_path = build_pdf_lookup(tender_id)
    rows = json.loads(cache_path.read_text(encoding="utf-8"))
    terms = [_normalise(term) for term in query.split() if term.strip()]
    results: list[PDFSnippet] = []
    for row in rows:
        text = row.get("text", "")
        hay = _normalise(text)
        score = sum(hay.count(term) for term in terms)
        if score <= 0:
            continue
        pos = _first_position(hay, terms)
        snippet = text[max(0, pos - 160): pos + 420].strip()
        results.append(PDFSnippet(tender_id, row.get("pdf_file", ""), row.get("page", 0), score, snippet))

    return [asdict(item) for item in sorted(results, key=lambda item: item.score, reverse=True)[:limit]]


def lookup_many(tender_id: str, fields: Iterable[str], limit_per_field: int = 3) -> dict:
    """Search several field names/values and return snippets grouped by query."""
    return {str(field): lookup_pdf_text(tender_id, str(field), limit_per_field) for field in fields if str(field).strip()}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def _first_position(text: str, terms: list[str]) -> int:
    positions = [text.find(term) for term in terms if term and text.find(term) >= 0]
    return min(positions) if positions else 0
