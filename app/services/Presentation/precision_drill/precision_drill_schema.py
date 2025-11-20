from pydantic import BaseModel
from typing import List, Optional


class PrecisionDrillRequest(BaseModel):
    wordlist: List[str]
class PrecisionDrillResponse(BaseModel):
    score:int
    feedback:str
    status:str
    message:str
    