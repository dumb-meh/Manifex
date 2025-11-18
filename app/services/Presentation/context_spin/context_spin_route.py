from fastapi import APIRouter, HTTPException, Header,UploadFile, File
from .context_spin import ContextSpin
from .context_spin import ContextSpinRequest, ContextSpinResponse
from app.utils.verify_auth import verify_token

router = APIRouter()
context_spin= ContextSpin()   

@router.post("/context_spin", response_model=ContextSpinResponse)
async def  get_context_spin(file:UploadFile = File(...),authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = context_spin.generate_context_spin(file)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))