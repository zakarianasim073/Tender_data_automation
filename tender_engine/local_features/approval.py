"""Local approval workflow: Draft -> Review -> Approved."""

from __future__ import annotations

import json
import pathlib
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parents[1]
INPUT_DIR = BASE / "input"
STATUSES = ["Draft", "Review", "Approved"]


def _path(tender_id: str) -> pathlib.Path:
    folder = INPUT_DIR / tender_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "approval.json"


def load_approval(tender_id: str) -> dict:
    p = _path(tender_id)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    data = {"tender_id": tender_id, "status": "Draft", "history": []}
    save_approval(tender_id, "Draft", "Created")
    return data


def save_approval(tender_id: str, status: str, note: str = "") -> dict:
    if status not in STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(STATUSES)}")
    p = _path(tender_id)
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"tender_id": tender_id, "history": []}
    data["status"] = status
    data.setdefault("history", []).append({"at": datetime.now().isoformat(timespec="seconds"), "status": status, "note": note})
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def kanban_board() -> dict:
    board = {s: [] for s in STATUSES}
    for folder in INPUT_DIR.glob("*"):
        if not folder.is_dir():
            continue
        data = load_approval(folder.name)
        board.setdefault(data["status"], []).append(folder.name)
    return board
