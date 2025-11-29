from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Body, Query
from .sight_word_practice import SightWordPractice
from .sight_word_practice_schema import SightWordRequest, SightWordResponse
from app.utils.verify_auth import verify_token

router = APIRouter()
sight_word_service = SightWordPractice()

@router.post("/sight_words", response_model=SightWordResponse)
async def get_sightwords(request_data: SightWordRequest = Body(...), user_id: str = Query(...), authtoken: str = Header(...)):
    if not verify_token(authtoken):
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = sight_word_service.generate_sentence(request_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




