from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List
from app.services.report_service import submission_report
from app.services.docx_service import render_template
from app.utils.helpers import create_submission_zip

router = APIRouter(prefix="/generate", tags=["generate"])


class ReportRequest(BaseModel):
    validation: Dict[str, Any]
    comparisons: Dict[str, Any]
    contractor: Dict[str, Any] | None = None


@router.post("/report")
def generate_report(req: ReportRequest):
    return submission_report(req.validation, req.comparisons, req.contractor)


class DocxRequest(BaseModel):
    template_name: str
    context: Dict[str, Any]
    output_name: str = "submission_output.docx"


@router.post("/docx")
def generate_docx(req: DocxRequest):
    path = render_template(
        f"backend/app/templates/word/{req.template_name}",
        req.context,
        f"backend/outputs/{req.output_name}",
    )
    return {"success": True, "path": path}


@router.post("/zip")
def export_zip(files: List[str]):
    zip_path = create_submission_zip(files)
    return {"success": True, "zip_path": zip_path}
