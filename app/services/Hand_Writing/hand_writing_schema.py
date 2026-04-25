from pydantic import BaseModel

class HandWritingResponse(BaseModel):
    correct: bool


class HandWritingWordsResponse(BaseModel):
    words: list[str]


