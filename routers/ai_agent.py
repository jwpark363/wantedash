from fastapi import APIRouter, UploadFile
import os
from pydantic import BaseModel
from agent.general_agent import chat

router = APIRouter()

class Item(BaseModel):
    message: str

@router.post("/chat")
async def for_student(item: Item):
    message = item.message
    print(message)
    ## 세션 처리 방법 고민 필요
    cfg = {"configurable" : {"session_id" : "student-123"}}
    result = chat(message,cfg)
    print(result)
    return result