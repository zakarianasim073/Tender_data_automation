"""
SOR Upload Management
---------------------
Stores uploaded SOR rate schedule PDFs locally and records the active BWDB/LGED
schedule paths in firm_config.json so the rate checker can use them.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "sor" / "uploads"
CONFIG_PATH = BASE_DIR / "context" / "firm_config.json"


def save_uploaded_sor(file_path: str, source: str) -> Dict[str, str]:
    source_key = source.strip().lower()
    if source_key not in {"bwdb", "lged"}:
        raise ValueError("source must be BWDB or LGED")

    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"SOR file not found: {file_path}")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = UPLOAD_DIR / f"{source_key.upper()}_{stamp}_{src.name}"
    shutil.copy2(src, dest)

    config = _load_config()
    config[f"sor_pdf_{source_key}"] = str(dest)
    config[f"sor_pdf_{source_key}_updated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_config(config)

    return {
        "source": source_key.upper(),
        "stored_path": str(dest),
        "config_path": str(CONFIG_PATH),
        "message": f"Saved {source_key.upper()} SOR schedule and updated firm_config.json",
    }


def active_sor_paths() -> Dict[str, str]:
    config = _load_config()
    return {
        "BWDB": config.get("sor_pdf_bwdb", ""),
        "LGED": config.get("sor_pdf_lged", ""),
    }


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    return {}


def _save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
