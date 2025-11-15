from pydantic import BaseModel
from typing import List, Optional

class SightWordRequest(BaseModel):
    grade_level: Optional[str] = "1"  # Grade level: 1-3
    num_words: Optional[int] = 3  # Number of sight words to include in sentence
    
class SightWordResponse(BaseModel):
    sentence: str
    sight_words: List[str]
    grade_level: str 