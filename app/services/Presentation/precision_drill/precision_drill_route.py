from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from .precision_drill import PrecisionDrill
from .precision_drill_schema import PrecisionDrillRequest, PrecisionDrillResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
import json

router = APIRouter()
precision_drill= PrecisionDrill()     

@router.post("/precision_drill", response_model=PrecisionDrillResponse)
async def  precision_drill_score(
    wordlist: str = Form(...),  # JSON string for list
    file: UploadFile = File(...),
    authtoken: str = Header(...)
):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        # Parse wordlist - support both JSON array and comma-separated formats
        try:
            # First try JSON parsing
            wordlist_parsed = json.loads(wordlist)
            if not isinstance(wordlist_parsed, list):
                raise ValueError("Wordlist must be a list")
        except (json.JSONDecodeError, ValueError):
            # Fall back to comma-separated parsing
            try:
                wordlist_parsed = [word.strip() for word in wordlist.split(',') if word.strip()]
                if not wordlist_parsed:
                    raise ValueError("Wordlist cannot be empty")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid wordlist format. Use JSON array like [\"word1\",\"word2\"] or comma-separated like \"word1,word2\": {str(e)}")
        
        # Create request object
        request = PrecisionDrillRequest(wordlist=wordlist_parsed)
        
        transcript = await convert_audio_to_text(file)
        response = precision_drill.precision_drill_score(request, transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_precision_drill")
async def  get_precision_drill(authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = precision_drill.generate_precision_drill()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))