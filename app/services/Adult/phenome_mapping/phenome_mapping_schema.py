from pydantic import BaseModel
from typing import List

class PhenomeMappingItem(BaseModel):
    word: str
    word_url: str
    options: list[str]
    correct_combination: list[int]  # Indices of options that when concatenated form the word

class PhenomeMappingResponse(BaseModel):
    exercises: List[PhenomeMappingItem]

