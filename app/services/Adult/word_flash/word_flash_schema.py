from pydantic import BaseModel
from typing import Optional

class WordFlashRequest(BaseModel):
    word: str

class WordFlashResponse(BaseModel):
    score: int = 0
    feedback: str = "No feedback available"
    status: str = "error"
    message: str = "Evaluation failed"
    
