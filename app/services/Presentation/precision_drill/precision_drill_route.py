from fastapi import APIRouter, HTTPException, Header,UploadFile, File
from .precision_drill import PrecisionDrill
from .precision_drill_schema import PrecisionDrillRequest, PrecisionDrillResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text

router = APIRouter()
precision_drill= PrecisionDrill()     

@router.post("/precision_drill", response_model=PrecisionDrillResponse)
async def  precision_drill_score(request:PrecisionDrillRequest,file:UploadFile = File(...),authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        transcript = await convert_audio_to_text(file)
        response = precision_drill.precision_drill_score(request, transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_precision_drill")
async def  get_precision_drill(authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = precision_drill.generate_precision_drill()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))