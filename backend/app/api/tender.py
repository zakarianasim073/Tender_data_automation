from pathlib import Path
import re
import shutil
import sys
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[3]
ENGINE_DIR = ROOT_DIR / "tender_engine"
INPUT_DIR = ENGINE_DIR / "input"
OUTPUT_DIR = ENGINE_DIR / "output"
TEMPLATE_DIR = ENGINE_DIR / "templates"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tender_engine.pipeline import run_pipeline  # noqa: E402

router = APIRouter(prefix="/tender", tags=["Tender Processing"])


class GeneratedFile(BaseModel):
    name: str
    url: str
    size_kb: float


class ProcessResponse(BaseModel):
    success: bool
    tender_id: str
    message: str
    output_folder: str
    files: List[GeneratedFile]


FIRM_CONFIG = {
    "firm_name": "M/S Hassan & Brothers",
    "firm_address": "Mahmud Tower (9th Floor) 19, Siddique Bazar North South Road, Bongshal, Dhaka",
    "proprietor_name": "Mahmudul Hassan",
    "egp_email": "info@handbl.com",
    "memo_no": "HB/",
    "bank_name": "SBAC Bank Limited",
    "bank_branch": "Gulshan Branch, Dhaka, Bangladesh",
    "bank_guarantee_no": "",
    "procuring_entity_short": "BWDB",
    "is_jv": False,
    "rate_schedule_ref": "BWDB, 2019-20 Rate Schedule",
    "work_months": ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
}


@router.post("/process", response_model=ProcessResponse)
async def process_tender(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Upload Notice, TDS, and BOQ PDF files.")

    pdf_files = [f for f in files if f.filename and f.filename.lower().endswith(".pdf")]
    if len(pdf_files) < 3:
        raise HTTPException(status_code=400, detail="At least Notice, TDS, and BOQ PDFs are required.")

    tender_id = _detect_tender_id([f.filename for f in pdf_files])
    input_folder = INPUT_DIR / tender_id
    input_folder.mkdir(parents=True, exist_ok=True)

    for upload in pdf_files:
        target = input_folder / _safe_filename(upload.filename)
        with target.open("wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)

    try:
        output_folder = run_pipeline(
            input_folder=str(input_folder),
            template_folder=str(TEMPLATE_DIR),
            output_base=str(OUTPUT_DIR),
            firm_config=FIRM_CONFIG,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Tender processing failed: {exc}") from exc

    generated = []
    for path in sorted(Path(output_folder).iterdir()):
        if path.is_file() and not path.name.startswith("~$"):
            generated.append(
                GeneratedFile(
                    name=path.name,
                    url=f"/generated/{tender_id}/{path.name}",
                    size_kb=round(path.stat().st_size / 1024, 1),
                )
            )

    return ProcessResponse(
        success=True,
        tender_id=tender_id,
        message=f"Generated {len(generated)} output files.",
        output_folder=str(output_folder),
        files=generated,
    )


@router.get("/outputs/{tender_id}")
def list_outputs(tender_id: str):
    folder = OUTPUT_DIR / _safe_filename(tender_id)
    if not folder.exists():
        raise HTTPException(status_code=404, detail="No generated outputs found for this tender ID.")
    return {
        "tender_id": tender_id,
        "files": [
            {
                "name": path.name,
                "url": f"/generated/{tender_id}/{path.name}",
                "size_kb": round(path.stat().st_size / 1024, 1),
            }
            for path in sorted(folder.iterdir())
            if path.is_file() and not path.name.startswith("~$")
        ],
    }


def _detect_tender_id(filenames: List[str]) -> str:
    joined = " ".join(filenames)
    match = re.search(r"(\d{5,})", joined)
    return match.group(1) if match else "manual-upload"


def _safe_filename(name: str) -> str:
    name = Path(name).name
    return re.sub(r"[^A-Za-z0-9._()\- ]+", "_", name).strip() or "uploaded.pdf"
