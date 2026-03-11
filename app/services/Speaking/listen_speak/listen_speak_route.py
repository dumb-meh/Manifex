from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form, Query
from .listen_speak import ListenSpeak
from .listen_speak_schema import ListenSpeakRequest, ListenSpeakResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
import json
router = APIRouter()
listen_speak= ListenSpeak()   

@router.post("/listen_speak", response_model=ListenSpeakResponse)
async def listen_speak_score(
    sentence: str = Form(...),
    file: UploadFile = File(...),
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        transcript = await convert_audio_to_text(file)
        print(f"[listen_speak_route] transcript: '{transcript['text']}' success={transcript.get('success')}")
        # early exit if no speech detected
        if not transcript['text'] or not transcript['text'].strip():
            print("[listen_speak_route] empty transcript detected, returning default response")
            return ListenSpeakResponse(score=0, feedback="No audio detected", status="success", message="Empty transcript", transcript=transcript['text'])
        request = ListenSpeakRequest(sentence=sentence)
        response = listen_speak.listen_speak_score(request, transcript['text'])
        try:
            response.transcript = transcript['text']
        except Exception:
            pass
        print(f"[listen_speak_route] evaluation response: {response}")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_listen_speak")
async def get_listen_speak(
    age: str = Query(...),
    user_id: str = Query(...),
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await listen_speak.generate_listen_speak(age)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))