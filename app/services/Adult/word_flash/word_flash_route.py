from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from .word_flash import WordFlash
from .word_flash_schema import WordFlashRequest, WordFlashResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
import json
router = APIRouter()
word_flash= WordFlash()

@router.post("/word_flash", response_model=WordFlashResponse)
async def word_flash_score(
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
        request = WordFlashRequest(word=word)
        response = word_flash.word_flash_score(request, transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_word_flash")
async def get_word_flash(
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = word_flash.generate_word_flash()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))