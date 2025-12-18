from pydantic import BaseModel
from typing import List

class SightWordRequest(BaseModel):
    age: str
    
class SightWordItem(BaseModel):
    word: str
    audio_url:str
    definition: List[str]
    sentence: str 
    quiz: List[str]  
    answer: str
    
class SightWordResponse(BaseModel):
    response: List[SightWordItem] = []