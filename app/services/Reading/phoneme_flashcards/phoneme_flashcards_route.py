from fastapi import APIRouter, HTTPException, Header, Query
from .phoneme_flashcards import PhonemeFlashcards
from .phoneme_flashcards_schema import PhonemeFlashcardsResponse
from app.utils.verify_auth import verify_token

router = APIRouter()
phoneme_flashcards_service = PhonemeFlashcards()

@router.get("/generate_phoneme_flashcards", response_model=PhonemeFlashcardsResponse)
async def generate_phoneme_flashcards(age: str = Query(..., description="Child's age (5-8)"), authtoken: str = Header(...)):
    # Verify authentication token
    if not verify_token(authtoken):
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    # Validate age
    if age not in ["5", "6", "7", "8"]:
        try:
            age_int = int(age)
            if age_int < 6:
                age = "5"
            elif age_int > 8:
                age = "8"
            else:
                age = str(age_int)
        except:
            age = "6"
    
    try:
        response = phoneme_flashcards_service.generate_flashcards(age)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))