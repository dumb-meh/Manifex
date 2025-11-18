from pydantic import BaseModel
from typing import Optional

class ContextSpinRequest(BaseModel):
    previous_secaniros: Optional[str]
    previous_words: Optional[list[str]]

class ContextSpinResponse(BaseModel):
    score:str
    feedback:str
    status:str
    message:str
    
