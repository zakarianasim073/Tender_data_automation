"""
File Manager
------------
Handles output folder creation, file copying, and path resolution.
"""

import shutil
import json
from pathlib import Path
from dataclasses import asdict


def ensure_output_folder(base_output: str, tender_id: str) -> Path:
    """Create and return output/tender_id/ folder."""
    folder = Path(base_output) / tender_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_json(tender_data, output_folder: Path, filename: str = "extracted_data.json"):
    """Serialise TenderData to JSON for inspection / re-use."""
    out_path = output_folder / filename
    data = asdict(tender_data)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved: {out_path.name}")
    return out_path


def resolve_template(template_dir: str, filename: str) -> Path:
    """Return full path to a template file, raising if missing."""
    p = Path(template_dir) / filename
    if not p.exists():
        raise FileNotFoundError(
            f"Template not found: {p}\n"
            f"Copy your master DOCX/XLSX templates into: {template_dir}"
        )
    return p


def output_path(folder: Path, filename_pattern: str, tender_data) -> Path:
    """Replace {{TENDER_ID}} etc. in filename pattern and return full path."""
    name = filename_pattern
    name = name.replace("{{TENDER_ID}}", tender_data.tender_id)
    name = name.replace("{{JV_NAME}}", tender_data.jv_name or "JV")
    return folder / name


def print_summary(output_folder: Path):
    """Print all files in the output folder."""
    files = sorted(output_folder.iterdir())
    print(f"\n{'='*60}")
    print(f"  Output folder: {output_folder}")
    print(f"  {len(files)} file(s) generated:")
    for f in files:
        size_kb = f.stat().st_size / 1024
        print(f"    >> {f.name}  ({size_kb:.1f} KB)")
    print(f"{'='*60}\n")
