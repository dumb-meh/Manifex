from pydantic import BaseModel
from typing import Optional

class ContextSpinRequest(BaseModel):
    scenario:str
    words: list[str]

class ContextSpinResponse(BaseModel):
    score:str
    feedback:str
    status:str
    message:str
    
