from fastapi import APIRouter
from pydantic import BaseModel
from app.services.extraction_service import extract_from_pdf

router = APIRouter(prefix="/extract", tags=["extract"])


class ExtractRequest(BaseModel):
    path: str
    language: str = "en"


@router.post("")
def extract(req: ExtractRequest):
    return extract_from_pdf(req.path, req.language)
