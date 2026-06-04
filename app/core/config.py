import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    MAX_CONVERSATION_HISTORY: int = 6
    CACHE_TTL_HOURS: int = 24
    RESPONSE_CACHE_TTL_HOURS: int = 24

settings = Settings()    