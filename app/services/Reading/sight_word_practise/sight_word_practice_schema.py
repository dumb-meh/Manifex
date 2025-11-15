from pydantic import BaseModel
from typing import List

class SightWordRequest(BaseModel):
    age: str  # Child's age (5-8)
    
class SightWordResponse(BaseModel):
    sentence: str
    sight_words: List[str]
    age: str 