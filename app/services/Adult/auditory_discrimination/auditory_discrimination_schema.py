from pydantic import BaseModel
from typing import Optional, Any

class AuditoryDiscriminationResponse(BaseModel):
    word_pairs: list[dict[str, Any]]
