from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from .context_spin import ContextSpin
from .context_spin_schema import ContextSpinRequest, ContextSpinResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
import json
router = APIRouter()
context_spin= ContextSpin()   

@router.post("/context_spin", response_model=ContextSpinResponse)
async def  context_spin_score(
    scenario: str = Form(...),
    words: str = Form(...),  # JSON string for list
    file: UploadFile = File(...),
    authtoken: str = Header(...)
):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        # Parse words - support both JSON array and comma-separated formats
        try:
            # First try JSON parsing
            words_list = json.loads(words)
            if not isinstance(words_list, list):
                raise ValueError("Words must be a list")
        except (json.JSONDecodeError, ValueError):
            # Fall back to comma-separated parsing
            try:
                words_list = [word.strip() for word in words.split(',') if word.strip()]
                if not words_list:
                    raise ValueError("Words list cannot be empty")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid words format. Use JSON array like [\"word1\",\"word2\"] or comma-separated like \"word1,word2\": {str(e)}")
        
        # Create request object
        request = ContextSpinRequest(scenario=scenario, words=words_list)
        
        transcript = await convert_audio_to_text(file)
        response = context_spin.context_spin_score(request,transcript['text'])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_context_spin")
async def  get_context_spin(authtoken: str = Header(...)):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = context_spin.generate_context_spin()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))