from fastapi import APIRouter
from app.services.validation_service import validate_tender_payload

router = APIRouter(prefix="/validate", tags=["validate"])

@router.post("")
def validate(payload: dict):
    return validate_tender_payload(payload)
