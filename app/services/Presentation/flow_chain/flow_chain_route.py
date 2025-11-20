from fastapi import APIRouter, HTTPException, Header,UploadFile, File
from .flow_chain import FlowChain
from .flow_chain import FlowChainRequest, FlowChainResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
router = APIRouter()
flow_chain= FlowChain()   

@router.post("/flow_chain", response_model=FlowChainResponse)
async def  flow_chain_score(request:FlowChainRequest ,file:UploadFile = File(...),authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        transcript = await convert_audio_to_text(file)
        response = flow_chain.flow_chain_score(request, transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_flow_chain")
async def  generate_flow_chain(authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = flow_chain.generate_flow_chain()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))