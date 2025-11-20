from pydantic import BaseModel
from typing import Optional

class FlowChainRequest(BaseModel):
    word_list: list[str]
    
class FlowChainResponse(BaseModel):
    score:int
    feedback:str
    status:str
    message:str
    
