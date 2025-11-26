from pydantic import BaseModel
from typing import List

class PhraseItem(BaseModel):
    phrase: str
    phrase_options: List[str]

class PhraseMakerResponse(BaseModel):
    phrases: List[PhraseItem] = []
    
