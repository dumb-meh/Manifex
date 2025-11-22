from pydantic import BaseModel
from typing import Optional

class PronunciationRequest(BaseModel):
    word: str

class PronunciationResponse(BaseModel):
    score: int = 0
    feedback: str = "No feedback available"
    status: str = "error"
    message: str = "Evaluation failed"
    
