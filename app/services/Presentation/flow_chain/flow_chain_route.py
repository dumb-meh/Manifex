from fastapi import APIRouter, HTTPException, Header,UploadFile, File
from .flow_chain import FlowChain
from .flow_chain import ContextSpinRequest, ContextSpinResponse
from app.utils.verify_auth import verify_token

router = APIRouter()
flow_chain= FlowChain()   

@router.post("/context_spin", response_model=ContextSpinResponse)
async def  get_context_spin(file:UploadFile = File(...),authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = flow_chain.generate_context_spin(file)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))