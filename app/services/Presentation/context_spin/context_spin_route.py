from fastapi import APIRouter, HTTPException, Header,UploadFile, File
from .context_spin import ContextSpin
from .context_spin import ContextSpinRequest, ContextSpinResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
router = APIRouter()
context_spin= ContextSpin()   

@router.post("/context_spin", response_model=ContextSpinResponse)
async def  get_context_spin(request:ContextSpinRequest,file:UploadFile = File(...),authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        transcript = await convert_audio_to_text(file)
        response = context_spin.context_spin_score(request,transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_context_spin", response_model=ContextSpinResponse)
async def  get_context_spin(authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = context_spin.context_spin_score()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))