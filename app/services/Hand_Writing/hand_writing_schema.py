from pydantic import BaseModel
from typing import Optional

class HandWritingResponse(BaseModel):
    correct: bool
