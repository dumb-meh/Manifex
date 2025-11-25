from pydantic import BaseModel

class PhenomeMappingResponse(BaseModel):
    word: str
    word_url: str
    options: list[str]

