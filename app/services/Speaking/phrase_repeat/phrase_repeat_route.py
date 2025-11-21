from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form, Query
from .listen_&_speak import PhraseRepeat
from .listen_&_speak_schema import PhraseRepeatRequest, PhraseRepeatResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
import json
router = APIRouter()
phrase_repeat= PhraseRepeat()   

@router.post("/context_spin", response_model=PhraseRepeatResponse)
async def  context_spin_score(
    word: str = Form(...)
    file: UploadFile = File(...),
    authtoken: str = Header(...)
):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")


    try:
        try:
            phrase_list = json.loads(phrases)
            if not isinstance(phrase_list, list):
                raise ValueError("Phrases must be a list")
        except (json.JSONDecodeError, ValueError):
            try:
                phrase_list = [phrase.strip() for phrase in phrases.split(',') if phrase.strip()]
                if not phrase_list:
                    raise ValueError("Phrase list cannot be empty")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid words format. Use JSON array like [\"phrase1\",\"phrase2\"] or comma-separated like \"phrase1,phrase2\": {str(e)}")
    
        transcript = await convert_audio_to_text(file)
        request = PhraseRepeatRequest(phrase_list=phrase_list)
        response = phrase_repeat.phrase_repeat_score(request,transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_context_spin", age:str=Query(...))
async def  get_phrase_repeat(authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = phrase_repeat.generate_phrase_repeat(age)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))