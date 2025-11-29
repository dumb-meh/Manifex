from fastapi import APIRouter, HTTPException, Body, Header, Query
from .writing import Writing
from .writing_schema import FinalScoreRequest, FinalScoreResponse, InitialTopicResponse, TopicRequest 
from app.utils.verify_auth import verify_token

router= APIRouter()
writing= Writing()

@router.post("/topic", response_model=InitialTopicResponse)
async def get_topic(request_data: TopicRequest = None,user_id: str = Query(...), authtoken: str = Header(...)):
    try:
        is_valid = verify_token(authtoken)
        if not is_valid:  # ✅ Explicitly check if token is valid
            raise HTTPException(status_code=401, detail="Invalid auth token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = writing.get_topic(request_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/final", response_model=FinalScoreResponse)
async def get_final_score(request_data: FinalScoreRequest, authtoken: str = Header(...)):
    try:
        is_valid = verify_token(authtoken)
        if not is_valid:  # ✅ Explicitly check if token is valid
            raise HTTPException(status_code=401, detail="Invalid auth token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = writing.get_writing_score(request_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))