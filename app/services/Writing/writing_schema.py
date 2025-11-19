from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class TopicEnum(str, Enum):
    SPORTS = "Sports"
    DANCE = "Dance"
    COOKING = "Cooking"
    FOOD = "Food"
    NATURE = "Nature"
    ART = "Art"
    MUSIC = "Music"
    TRAVEL = "Travel"
    SCIENCE = "Science"
    MOVIES = "Movies"
    MEDITATION = "Meditation"
    GAMING = "Gaming"
    ANIMALS = "Animals"

class TopicRequest(BaseModel):
    topic: Optional[TopicEnum] = None  # If None, a random topic will be selected
    age:str

class InitialTopicResponse(BaseModel):
    topic: str
    related_words: List[str]


class FinalScoreRequest(BaseModel):
    topic: str
    related_words: List[str]
    user_paragraph: str

class FinalScoreResponse(BaseModel):
    sentence_score: int  # Score out of 10 for overall writing quality
    motivation: str  # Motivational message and feedback