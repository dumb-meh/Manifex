from pydantic import BaseModel
from typing import Optional

class HandWritingResponse(BaseModel):
    correct: bool
    image_url: Optional[str] = None
