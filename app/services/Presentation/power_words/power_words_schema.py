from pydantic import BaseModel

class PowerWordsRequest(BaseModel):
    word:str

class PowerWordsResponse(BaseModel):
    score:int
    feedback:str
    status:str
    message:str
    