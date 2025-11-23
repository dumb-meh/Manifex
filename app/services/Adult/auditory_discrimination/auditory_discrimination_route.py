from fastapi import APIRouter, HTTPException, Header
from .auditory_discrimination_schema import AuditoryDiscriminationResponse
from .auditory_discrimination import AuditoryDiscrimination
from app.utils.verify_auth import verify_token

import json
router = APIRouter()
auditory_discrimination= AuditoryDiscrimination()


@router.get("/get_auditory_discrimination", response_model=AuditoryDiscriminationResponse)
async def get_auditory_discrimination(
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await auditory_discrimination.get_auditory_discrimination()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))