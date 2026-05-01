"""Filesystem cache for parsed/generated tender summaries."""

from __future__ import annotations

import json
import pathlib
import time

BASE = pathlib.Path(__file__).resolve().parents[1]
CACHE_DIR = BASE / "cache"
TTL_SECONDS = 24 * 60 * 60


def _path(tender_id: str) -> pathlib.Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{tender_id}.json"


def save_cache(tender_id: str, data: dict) -> str:
    payload = {"saved_at": time.time(), "tender_id": tender_id, "data": data}
    p = _path(tender_id)
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(p)


def load_cache(tender_id: str, ttl_seconds: int = TTL_SECONDS) -> dict | None:
    p = _path(tender_id)
    if not p.exists():
        return None
    payload = json.loads(p.read_text(encoding="utf-8"))
    if time.time() - payload.get("saved_at", 0) > ttl_seconds:
        return None
    return payload.get("data")


def list_cached_tenders() -> list[dict]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in sorted(CACHE_DIR.glob("*.json")):
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            rows.append({"tender_id": payload.get("tender_id", p.stem), "saved_at": payload.get("saved_at", 0)})
        except Exception:
            continue
    return rows
