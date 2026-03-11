from pydantic import BaseModel
from typing import Optional

class ContextSpinRequest(BaseModel):
    scenario:str
    words: list[str]

class ContextSpinResponse(BaseModel):
    score:int
    feedback:str
    status:str
    message:str
    # optional field for debugging purposes
    transcript: Optional[str] = None
    
