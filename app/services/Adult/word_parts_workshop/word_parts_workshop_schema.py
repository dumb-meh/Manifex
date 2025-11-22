from pydantic import BaseModel
from typing import Optional

class WordPartsResponse(BaseModel):
    suffix: list[str] = []
    root: list[str] = []
    prefix: list[str] = []
    suffix_meaning: list[str] = []
    root_meaning: list[str] = []
    prefix_meaning: list[str] = []
    
