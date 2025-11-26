from pydantic import BaseModel
from typing import List

class SentenceItem(BaseModel):
    sentence: str
    sentence_options: List[str]

class SentenceBuilderResponse(BaseModel):
    sentences: List[SentenceItem] = []
    
