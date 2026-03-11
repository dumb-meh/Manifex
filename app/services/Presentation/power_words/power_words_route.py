from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form, Query
from .power_words import PowerWords
from .power_words_schema import PowerWordsRequest, PowerWordsResponse
from app.utils.verify_auth import verify_token
from app.utils.speech_to_text import convert_audio_to_text
router = APIRouter()
power_words= PowerWords()     

@router.post("/power_words", response_model=PowerWordsResponse)
async def  power_words_score(
    word: str = Form(...),
    defintion_file: UploadFile = File(...),
    sentence_file: UploadFile = File(...),
    authtoken: str = Header(...)
):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        # Create request object
        request = PowerWordsRequest(word=word)
        
        defintion = await convert_audio_to_text(defintion_file)
        sentence = await convert_audio_to_text(sentence_file)
        print(f"[power_words_route] definition transcript: '{defintion['text']}', sentence transcript: '{sentence['text']}'")
        if (not defintion['text'] or not defintion['text'].strip()) and (not sentence['text'] or not sentence['text'].strip()):
            print("[power_words_route] detected both transcripts empty, returning default low score")
            return PowerWordsResponse(score=0, feedback="No audio detected", status="success", message="Empty transcripts", transcript="")
        response = power_words.power_words_score(request,defintion['text'],sentence['text'])
        try:
            # store both pieces joined for easy debugging
            response.transcript = f"definition:{defintion['text']}|sentence:{sentence['text']}"
        except Exception:
            pass
        print(f"[power_words_route] evaluation response: {response}")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_power_words")
async def  generate_power_words(
    user_id: str = Query(...),
    authtoken: str = Header(...)
):
    try:
        authtoken=verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    try:
        response = power_words.generate_power_words()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))