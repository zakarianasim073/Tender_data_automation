from fastapi import APIRouter, UploadFile, File
from app.utils.helpers import ensure_dir
from pathlib import Path

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    ensure_dir("backend/uploads")
    p = Path("backend/uploads") / file.filename
    p.write_bytes(await file.read())
    return {"success": True, "filename": file.filename, "path": str(p)}
