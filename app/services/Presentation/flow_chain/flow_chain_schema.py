from pydantic import BaseModel
from typing import Optional


class FlowChainResponse(BaseModel):
    score:str
    feedback:str
    status:str
    message:str
    
