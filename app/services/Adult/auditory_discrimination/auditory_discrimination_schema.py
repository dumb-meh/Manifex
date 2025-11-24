from pydantic import BaseModel
from typing import Optional, Any

class AuditoryDiscriminationResponse(BaseModel):
    word_pairs: list[list[dict[str, Any]]]
