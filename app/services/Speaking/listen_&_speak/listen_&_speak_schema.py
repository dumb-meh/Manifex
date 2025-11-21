from pydantic import BaseModel
from typing import Optional

class ContextSpinRequest(BaseModel):
    words: str

class ContextSpinResponse(BaseModel):
    score:int
    feedback:str
    status:str
    message:str
    
