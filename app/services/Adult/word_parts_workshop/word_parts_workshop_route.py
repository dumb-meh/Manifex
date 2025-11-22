from fastapi import APIRouter, HTTPException, Header, Query
from .word_parts_workshop import WordPartsWorkshop
from .word_parts_workshop_schema import WordPartsResponse
from app.utils.verify_auth import verify_token
import json
router = APIRouter()
word_parts_workshop = WordPartsWorkshop()


    
@router.get("/get_word_parts", response_model=WordPartsResponse)
async def get_word_parts(
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = word_parts_workshop.word_parts_score()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))