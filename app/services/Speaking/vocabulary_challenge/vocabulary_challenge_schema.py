from pydantic import BaseModel
from typing import Optional

class VocabularyRequest(BaseModel):
    word: str

class VocabularyResponse(BaseModel):
    score: int = 0
    feedback: str = "No feedback available"
    status: str = "error"
    message: str = "Evaluation failed"
    
