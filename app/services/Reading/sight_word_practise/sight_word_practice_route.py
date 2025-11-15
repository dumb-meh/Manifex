from fastapi import APIRouter, HTTPException, Body
from .sight_word_practice import SightWordPractice
from .sight_word_practice_schema import SightWordRequest, SightWordResponse

router = APIRouter()
sight_word_service = SightWordPractice()

@router.post("/sight_words", response_model=SightWordResponse)
async def get_sightwords(request_data: SightWordRequest = Body(...)):
    try:
        result = sight_word_service.generate_sentence(request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))