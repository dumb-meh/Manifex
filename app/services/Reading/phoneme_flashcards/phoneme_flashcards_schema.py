from pydantic import BaseModel
from typing import List

class PhonemeFlashcardsResponse(BaseModel):
    word: str
    characters: List[str]  # Individual letters like ["P", "L", "A", "Y"]
    age: str

    