from fastapi import APIRouter, HTTPException, Header,UploadFile, File
from .power_words import PowerWords
from .power_words_schema import PowerWordsRequest, PowerWordsResponse
from app.utils.verify_auth import verify_token

router = APIRouter()
power_words= PowerWords()     

@router.post("/power_words", response_model=PowerWordsResponse)
async def  get_power_words(file:UploadFile = File(...),authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = power_words.generate_power_words()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))