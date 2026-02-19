from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from .hand_writing_schema import HandWritingResponse
from .hand_writing import HandWritingChecker
from app.utils.verify_auth import verify_token

router = APIRouter()
hand_writing_checker = HandWritingChecker()


@router.post("/check_handwriting", response_model=HandWritingResponse)
async def check_handwriting(
    image: UploadFile = File(..., description="Image file containing handwritten text"),
    word: str = Form(..., description="The word to match against"),
    authtoken: str = Header(...)
):
    try:
        verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await hand_writing_checker.check_handwriting(image, word)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))