from pydantic import BaseModel
from typing import List

class SightWordRequest(BaseModel):
    age: str  # Child's age (5-8)
    
class SightWordResponse(BaseModel):
    word: str
    definition: List[str]
    sentence: str 
    quiz: List[str]  
    answer: str