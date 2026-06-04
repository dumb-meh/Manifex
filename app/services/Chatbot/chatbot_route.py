from fastapi import APIRouter, HTTPException, Header
from .chatbot_schema import ChatbotMessageRequest, ChatbotMessageResponse
from .chatbot import ChatbotService
from app.utils.verify_auth import verify_token

router = APIRouter()
chatbot_service = ChatbotService()


@router.post("/", response_model=ChatbotMessageResponse)
async def chatbot_message(
    request: ChatbotMessageRequest,
    authtoken: str = Header(...)
):
    try:
        is_valid = verify_token(authtoken)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid auth token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid auth token")

    try:
        response = chatbot_service.get_response(request.user_id, request.user_message)
        return ChatbotMessageResponse(chatbot_reply=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))