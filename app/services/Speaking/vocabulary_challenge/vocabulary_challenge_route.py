from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form, Query
from .vocabulary_challenge import VocabularyChallenge
from .vocabulary_challenge_schema import VocabularyRequest, VocabularyResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
import json
router = APIRouter()
vocabulary_challenge= VocabularyChallenge()   

@router.post("/vocabulary_challenge", response_model=VocabularyResponse)
async def vocabulary_challenge_score(
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
        print(f"[vocabulary_challenge_route] transcript: '{transcript['text']}' success={transcript.get('success')}")
        if not transcript['text'] or not transcript['text'].strip():
            print("[vocabulary_challenge_route] empty transcript detected, returning default response")
            return VocabularyResponse(score=0, feedback="No audio detected", status="success", message="Empty transcript", transcript=transcript['text'])
        request = VocabularyRequest(word=word)
        response = vocabulary_challenge.vocabulary_score(request, transcript['text'])
        try:
            response.transcript = transcript['text']
        except Exception:
            pass
        print(f"[vocabulary_challenge_route] evaluation response: {response}")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_vocabulary")
async def get_vocabulary(
    age: str = Query(...),
    user_id: str = Query(...),
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await vocabulary_challenge.generate_vocabulary(age)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))