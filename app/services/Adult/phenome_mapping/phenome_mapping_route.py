from fastapi import APIRouter, HTTPException, Header
from .phenome_mapping_schema import PhenomeMappingResponse
from .phenome_mapping import PhenomeMapping
from app.utils.verify_auth import verify_token

import json
router = APIRouter()
phenome_mapping = PhenomeMapping()


@router.get("/get_phenome_mapping", response_model=PhenomeMappingResponse)
async def get_phenome_mapping(
    authtoken: str = Header(...)
):
    try:
        authtoken = verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await phenome_mapping.get_phenome_mapping()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))