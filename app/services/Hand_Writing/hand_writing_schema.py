from pydantic import BaseModel, Field

class HandWritingResponse(BaseModel):
    correct: bool


class HandWritingScoreResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)


class HandWritingWordsResponse(BaseModel):
    words: list[str]


