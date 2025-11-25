from pydantic import BaseModel
from typing import List

class PhenomeMappingItem(BaseModel):
    word: str
    word_url: str
    options: list[str]

class PhenomeMappingResponse(BaseModel):
    exercises: List[PhenomeMappingItem]

