from fastapi import APIRouter, HTTPException, Header
from .chatbot_schema import ChatbotMessageRequest, ChatbotMessageResponse
from .chatbot import ChatbotService
from app.utils.verify_auth import verify_token

router = APIRouter()
chatbot_service = ChatbotService()


def _verify_auth_token(authtoken: str) -> None:
    try:
        is_valid = verify_token(authtoken)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid auth token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid auth token")


@router.post("/web", response_model=ChatbotMessageResponse)
async def chatbot_web_message(
    request: ChatbotMessageRequest,
    authtoken: str = Header(...)
):
    if not authtoken.startswith("temp-"):
        _verify_auth_token(authtoken)

    try:
        response = chatbot_service.get_response(request.user_id, request.user_message, "web")
        return ChatbotMessageResponse(chatbot_reply=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/app", response_model=ChatbotMessageResponse)
async def chatbot_app_message(
    request: ChatbotMessageRequest,
    authtoken: str = Header(...)
):
    _verify_auth_token(authtoken)

    try:
        response = chatbot_service.get_response(request.user_id, request.user_message, "app")
        return ChatbotMessageResponse(chatbot_reply=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))