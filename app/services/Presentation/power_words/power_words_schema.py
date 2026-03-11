from pydantic import BaseModel
from typing import Optional

class PowerWordsRequest(BaseModel):
    word:str

class PowerWordsResponse(BaseModel):
    score:int
    feedback:str
    status:str
    message:str
    # debug transcript so frontend can see what was recognized
    transcript: Optional[str] = None
    