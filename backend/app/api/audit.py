from fastapi import APIRouter
from app.services.audit_service import build_audit

router = APIRouter(prefix="/audit", tags=["audit"])

@router.post("")
def audit(event: str, actor: str, details: dict):
    return build_audit(event, actor, details)
