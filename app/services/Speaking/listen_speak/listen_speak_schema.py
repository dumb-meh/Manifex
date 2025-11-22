from pydantic import BaseModel
from typing import Optional

class ListenSpeakRequest(BaseModel):
    sentence: str

class ListenSpeakResponse(BaseModel):
    score: int = 0
    feedback: str = "No feedback available"
    status: str = "error"
    message: str = "Evaluation failed"
    
