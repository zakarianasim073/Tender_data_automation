from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.security import create_token
import datetime

router = APIRouter(prefix="/license", tags=["License"])


class VerifyRequest(BaseModel):
    key: str
    hardware_id: str


LICENSE_DB = {
    "DEMO-123": {"expiry": "2099-12-31", "hw_id": "ANY", "plan": "pro"},
    "STARTUP-01": {"expiry": "2026-12-31", "hw_id": "ANY", "plan": "enterprise"},
}


@router.post("/verify")
def verify_license(data: VerifyRequest):
    record = LICENSE_DB.get(data.key)
    if not record:
        raise HTTPException(status_code=400, detail="Invalid License Key")

    if record["hw_id"] != "ANY" and record["hw_id"] != data.hardware_id:
        raise HTTPException(status_code=400, detail="Hardware ID Mismatch")

    expiry = datetime.datetime.strptime(record["expiry"], "%Y-%m-%d").date()
    if datetime.date.today() > expiry:
        raise HTTPException(status_code=400, detail="License Expired")

    token = create_token(user_id=data.key, plan=record["plan"])
    return {
        "valid": True,
        "token": token,
        "plan": record["plan"],
        "expires_at": record["expiry"],
    }
