from pydantic import BaseModel
from typing import List

class QuestionAnswer(BaseModel):
    question: str
    options: List[str]  # List of 3 options
    correct_answer: str  # The correct option

class ReadingComprehensionResponse(BaseModel):
    passage_name: str
    text: str
    questions: List[QuestionAnswer]
    age: str #### No need for age in response . Instead it is only necessary in input
    image: str = ""  # Optional image URL