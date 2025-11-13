from pydantic import BaseModel
from typing import List, Optional
from fastapi import Header

class PrecisionDrillRequest(BaseModel):
    transcript: str

class PrecisionDrillResponse(BaseModel):
    score:str
    feedback:str
    status:str
    message:str
    