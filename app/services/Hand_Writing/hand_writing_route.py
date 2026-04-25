from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form, Query
from .hand_writing_schema import HandWritingResponse, HandWritingWordsResponse
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
    

@router.post("/get_handwriting_words", response_model=HandWritingWordsResponse)
async def get_handwriting_words(
    user_id: str = Query(..., description="User id for word cache"),
    authtoken: str = Header(...)
):
    try:
        verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await hand_writing_checker.get_handwriting_words(user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


@router.post("/check_handwriting_words", response_model=HandWritingResponse)
async def check_handwriting_words(
    image: UploadFile = File(..., description="Image file containing handwritten text"),
    word: str = Form(..., description="The word to match against"),
    authtoken: str = Header(...)
):
    try:
        verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await hand_writing_checker.check_handwriting_words(image, word)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))