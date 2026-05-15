from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class TenderField(BaseModel):
    key: str
    value: str
    confidence: float = Field(default=0.0, ge=0, le=1)


class ContractorProfile(BaseModel):
    contractor_id: str
    name: str
    past_projects: int = 0
    blacklist_flag: bool = False


class TenderDocument(BaseModel):
    tender_id: str
    title: str
    language: str = "en"
    procuring_entity: Optional[str] = None
    fields: List[TenderField] = Field(default_factory=list)
    contractor: Optional[ContractorProfile] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
