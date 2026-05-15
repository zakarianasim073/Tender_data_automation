from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.security import create_token
from ..database.session import get_db
from ..models.database_models import License
import datetime

router = APIRouter(prefix="/license", tags=["License"])

class VerifyRequest(BaseModel):
    key: str
    hardware_id: str

@router.post("/verify")
def verify_license(data: VerifyRequest, db: Session = Depends(get_db)):
    record = db.query(License).filter(License.key == data.key).first()

    if not record:
        # Check hardcoded demo for backward compatibility or initial setup
        if data.key == "DEMO-123":
            return {
                "valid": True,
                "token": create_token(user_id=data.key, plan="pro"),
                "plan": "pro",
                "expires_at": "2099-12-31",
            }
        raise HTTPException(status_code=400, detail="Invalid License Key")

    if record.hw_id != "ANY" and record.hw_id != data.hardware_id:
        raise HTTPException(status_code=400, detail="Hardware ID Mismatch")

    if datetime.date.today() > record.expiry.date():
        raise HTTPException(status_code=400, detail="License Expired")

    token = create_token(user_id=data.key, plan=record.plan)
    return {
        "valid": True,
        "token": token,
        "plan": record.plan,
        "expires_at": record.expiry.isoformat(),
    }
