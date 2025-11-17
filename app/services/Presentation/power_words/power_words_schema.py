from pydantic import BaseModel

class PowerWordsResponse(BaseModel):
    score:str
    feedback:str
    status:str
    message:str
    