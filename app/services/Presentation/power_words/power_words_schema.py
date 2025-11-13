from pydantic import BaseModel
from typing import List, Optional
from fastapi import Header

class PowerWordsRequest(BaseModel):
    transcript: str

class PowerWordsResponse(BaseModel):
    score:str
    feedback:str
    status:str
    message:str
    