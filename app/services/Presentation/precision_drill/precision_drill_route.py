from fastapi import APIRouter, HTTPException, Header,UploadFile, File
from .precision_drill import PrecisionDrill
from .precision_drill_schema import PrecisionDrillRequest, PrecisionDrillResponse

router = APIRouter()
precision_drill= PrecisionDrill()     

@router.post("/precision_drill", response_model=PrecisionDrillResponse)
async def  get_precision_drill(file:UploadFile = File(...),authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = precision_drill.generate_precision_drill()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))