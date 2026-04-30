from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.core.gpt_client import GPTClient
from app.core.security import get_current_user

router = APIRouter(prefix="/gpt", tags=["GPT"])

class ChatMsg(BaseModel): role: str; content: str
class ChatReq(BaseModel): messages: List[ChatMsg]; language: Optional[str] = "en"

@router.post("/chat")
async def chat(req: ChatReq, user: dict = Depends(get_current_user)):
    gpt = GPTClient()
    res = await gpt.chat(user["id"], [m.model_dump() for m in req.messages], req.language)
    if not res["success"]: raise Exception(res.get("error"))
    return res
