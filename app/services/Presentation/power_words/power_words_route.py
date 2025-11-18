from fastapi import APIRouter, HTTPException, Header,UploadFile, File
from .power_words import PowerWords
from .power_words_schema import PowerWordsRequest, PowerWordsResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
router = APIRouter()
power_words= PowerWords()     

@router.post("/power_words", response_model=PowerWordsResponse)
async def  get_power_words(request: PowerWordsRequest, defintion_file:UploadFile = File(...),sentence_file:UploadFile = File(...),authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        defintion = await convert_audio_to_text(defintion_file)
        sentence = await convert_audio_to_text(sentence_file)
        response = power_words.power_words_score(request,defintion['text'],sentence['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_power_words", response_model=PowerWordsResponse)
async def  generate_power_words(authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = power_words.generate_power_words()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))