from pydantic import BaseModel, Field
from typing import Optional

class BOQItem(BaseModel):
    item_no: str
    description: str
    unit: str = "Nos"
    quantity: float = Field(default=0, ge=0)
    rate: float = Field(default=0, ge=0)

class BOQDelta(BaseModel):
    item_no: str
    status: str
    rate_a: Optional[float] = None
    rate_b: Optional[float] = None
