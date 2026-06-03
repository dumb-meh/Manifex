from fastapi import APIRouter, HTTPException, Header
from .chatbot_schema import ChatbotMessageRequest, ChatbotMessageResponse
from .hand_writing import HandWritingChecker
from app.utils.verify_auth import verify_token

router = APIRouter()
chatbot = Chatbot()


@router.post("/chatbot", response_model=ChatbotMessageResponse)
async def chatbot_message(
    request: ChatbotMessageRequest,
    authtoken: str = Header(...)
):
    try:
        verify_token(authtoken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid auth token")
    
    try:
        response = await chatbot.get_response(request.user_message)
        return ChatbotMessageResponse(chatbot_reply=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))