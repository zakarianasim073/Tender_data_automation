from datetime import datetime
import json
from pathlib import Path


def build_audit(event: str, actor: str, details: dict):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "actor": actor,
        "details": details,
    }
    out_dir = Path("backend/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    file = out_dir / f"audit_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
    with file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return payload
