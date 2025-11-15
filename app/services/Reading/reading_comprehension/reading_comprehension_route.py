from fastapi import APIRouter, HTTPException, Header, Query
from .reading_comprehension import ReadingComprehension
from .reading_comprehension_schema import ReadingComprehensionResponse
from app.utils.verify_auth import verify_token

router = APIRouter()
reading_comprehension_service = ReadingComprehension()

@router.get("/generate_comprehension", response_model=ReadingComprehensionResponse)
async def generate_comprehension(age: str = Query(..., description="Child's age (5-8)"), authtoken: str = Header(...)):
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
        response = reading_comprehension_service.generate_comprehension(age)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))