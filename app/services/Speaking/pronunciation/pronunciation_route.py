from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form, Query
from .pronunciation import Pronunciation
from .pronunciation_schema import PronunciationRequest, PronunciationResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
import json
router = APIRouter()
pronunciation= Pronunciation()   

@router.post("/pronunciation", response_model=PronunciationResponse)
async def pronunciation_score(
    word: str = Form(...),
    file: UploadFile = File(...),
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        transcript = await convert_audio_to_text(file)
        request = PronunciationRequest(word=word)
        response = pronunciation.pronunciation_score(request, transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_pronunciation")
async def get_pronunciation(
    age: str = Query(...),
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await pronunciation.generate_pronunciation(age)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))