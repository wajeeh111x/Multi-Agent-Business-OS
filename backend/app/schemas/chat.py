from pydantic import BaseModel
from typing import List, Dict, Any

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]