from typing import List, Optional
from pydantic import BaseModel

class ChatbotMessageRequest:
    past_conversations: Optional[List[dict]] = None
    user_message: str

class ChatbotMessageResponse:
    chatbot_reply: str