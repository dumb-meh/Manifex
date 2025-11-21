from pydantic import BaseModel
from typing import Optional

class PhraseRepeatRequest(BaseModel):
    phrase_list: list[str]

class PhraseRepeatResponse(BaseModel):
    score:int
    feedback:str
    status:str
    message:str
    
