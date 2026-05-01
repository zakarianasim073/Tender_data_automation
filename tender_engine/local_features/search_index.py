"""Simple local full-text search across generated tender packs."""

from __future__ import annotations

import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE / "output"
INDEX_PATH = BASE / "cache" / "search_index.json"
TEXT_EXTS = {".txt", ".json", ".md", ".csv"}


def build_search_index() -> str:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    docs = []
    for tender_dir in OUTPUT_DIR.glob("*"):
        if not tender_dir.is_dir():
            continue
        for file in tender_dir.iterdir():
            if not file.is_file() or file.suffix.lower() not in TEXT_EXTS:
                continue
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            docs.append({
                "tender_id": tender_dir.name,
                "file": file.name,
                "path": str(file),
                "text": text[:200000],
            })
    INDEX_PATH.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
    return str(INDEX_PATH)


def search_tenders(query: str, limit: int = 50) -> list[dict]:
    if not INDEX_PATH.exists():
        build_search_index()
    docs = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    terms = [t.lower() for t in query.split() if t.strip()]
    results = []
    for doc in docs:
        hay = doc["text"].lower()
        score = sum(hay.count(term) for term in terms)
        if score:
            snippet_start = min([hay.find(t) for t in terms if hay.find(t) >= 0] or [0])
            snippet = doc["text"][max(0, snippet_start - 80): snippet_start + 220]
            results.append({**{k: doc[k] for k in ["tender_id", "file", "path"]}, "score": score, "snippet": snippet})
    return sorted(results, key=lambda r: r["score"], reverse=True)[:limit]
