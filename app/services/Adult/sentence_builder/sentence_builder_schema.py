from pydantic import BaseModel

class SentenceBuilderResponse(BaseModel):
    sentences: list[list[str]] = []
    
