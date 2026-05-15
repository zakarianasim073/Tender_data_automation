from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def create_submission_zip(files: list[str]) -> str:
    ensure_dir("backend/outputs")
    zip_path = Path("backend/outputs") / f"submission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zf:
        for file in files:
            p = Path(file)
            if p.exists() and p.is_file():
                zf.write(p, arcname=p.name)
    return str(zip_path)
