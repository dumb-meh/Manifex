from fastapi import APIRouter, HTTPException, Header, Query
from .phoneme_flashcards import PhonemeFlashcards
from .phoneme_flashcards_schema import PhonemeFlashcardsResponse
from app.utils.verify_auth import verify_token

router = APIRouter()

@router.get("/generate_phoneme_flashcards", response_model=PhonemeFlashcardsResponse)
async def generate_phoneme_flashcards(age: str = Query(..., description="Child's age "), user_id: str = Query(...), authtoken: str = Header(...)):
    # Verify authentication token
    if not verify_token(authtoken):
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        print(f"[PHONEME_ROUTE] Received request with age: {age} (type: {type(age)})")
        
        # Create fresh instance for each request to avoid caching issues
        phoneme_flashcards_service = PhonemeFlashcards()
        response = phoneme_flashcards_service.generate_flashcards(age)
        
        print(f"[PHONEME_ROUTE] Generated response - word: {response.word}, age: {response.age}, word_length: {len(response.word)}")
        
        return response
    except Exception as e:
        print(f"[PHONEME_ROUTE] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))