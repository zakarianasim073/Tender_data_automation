from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

router = APIRouter()

class ItemData(BaseModel):
    item: str = Field(..., min_length=1)
    rate: float = Field(..., ge=0)
    quantity: Optional[float] = Field(default=1.0, ge=0)

    @field_validator("item")
    @classmethod
    def strip_item(cls, value: str) -> str:
        return value.strip()

class BOQRequest(BaseModel):
    boq: List[ItemData]
    sor: List[ItemData]

@router.post("/diff")
def visual_diff(data: BOQRequest):
    sor_map = {i.item.strip().lower(): i for i in data.sor}
    result = []
    for b in data.boq:
        key = b.item.strip().lower()
        s = sor_map.get(key)
        if not s:
            status, color = "missing", "#fca5a5"
        elif abs(b.rate - s.rate) > 0.01:
            status, color = "mismatch", "#fbbf24"
        else:
            status, color = "match", "#86efac"
        result.append({"item": b.item.strip(), "boq_rate": b.rate, "sor_rate": s.rate if s else None, "status": status, "color": color})
    return {"success": True, "count": len(result), "data": result}
