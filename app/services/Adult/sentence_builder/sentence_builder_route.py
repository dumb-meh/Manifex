from fastapi import APIRouter, HTTPException, Header, Query
from .sentence_builder import SentenceBuilder
from .sentence_builder_schema import SentenceBuilderResponse
from app.utils.verify_auth import verify_token
import json
router = APIRouter()
sentence_builder = SentenceBuilder()

@router.get("/get_sentences", response_model=SentenceBuilderResponse)
async def get_sentences(
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = sentence_builder.get_sentences()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))