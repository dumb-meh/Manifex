from pydantic import BaseModel

class PhraseMakerResponse(BaseModel):
    phrases: list[list[str]] = []
    
