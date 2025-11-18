from pydantic import BaseModel

class PowerWordsRequest(BaseModel):
    word:str

class PowerWordsResponse(BaseModel):
    score:str
    feedback:str
    status:str
    message:str
    