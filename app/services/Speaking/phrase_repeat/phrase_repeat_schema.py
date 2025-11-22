from pydantic import BaseModel
from typing import Optional

class PhraseRepeatRequest(BaseModel):
    phrase: str

class PhraseRepeatResponse(BaseModel):
    score: int = 0
    feedback: str = "No feedback available"
    status: str = "error"
    message: str = "Evaluation failed"
    
