from fastapi import APIRouter, HTTPException, Header, Query
from .phrase_maker import PhraseMaker
from .phrase_maker_schema import PhraseMakerResponse
from app.utils.verify_auth import verify_token
import json
router = APIRouter()
phrase_maker = PhraseMaker()

@router.get("/get_phrases", response_model=PhraseMakerResponse)
async def get_phrases(
    user_id: str = Query(...),
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = phrase_maker.get_phrases()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))