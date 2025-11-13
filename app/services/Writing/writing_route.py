from fastapi import APIRouter, HTTPException, Body
from .writing import Writing
from .writing_schema import FinalScoreRequest, FinalScoreResponse, InitialTopicResponse, TopicRequest

router= APIRouter()
writing= Writing()

@router.post("/topic", response_model=InitialTopicResponse)
async def get_topic(request_data: TopicRequest = None):
    try:
        response = writing.get_topic(request_data)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/final", response_model=FinalScoreResponse)
async def get_final_score(request_data: FinalScoreRequest):
    try:
        response = writing.get_writing_score(request_data)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    