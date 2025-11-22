from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form, Query
from .phrase_repeat import PhraseRepeat
from .phrase_repeat_schema import PhraseRepeatRequest, PhraseRepeatResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
import json
router = APIRouter()
phrase_repeat = PhraseRepeat()   

@router.post("/phrase_repeat", response_model=PhraseRepeatResponse)
async def phrase_repeat_score(
    phrases: str = Form(...),
    file: UploadFile = File(...),
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")

    try:
        # Parse phrases input (JSON or comma-separated)
        try:
            phrase_list = json.loads(phrases)
            if not isinstance(phrase_list, list):
                raise ValueError("Phrases must be a list")
        except (json.JSONDecodeError, ValueError):
            phrase_list = [phrase.strip() for phrase in phrases.split(',') if phrase.strip()]
            if not phrase_list:
                raise HTTPException(status_code=400, detail="Phrase list cannot be empty")
    
        transcript = await convert_audio_to_text(file)
        request = PhraseRepeatRequest(phrase_list=phrase_list)
        response = phrase_repeat.phrase_repeat_score(request, transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_phrase_repeat")
async def get_phrase_repeat(
    age: str = Query(...),
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await phrase_repeat.generate_phrase_repeat(age)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))