from typing import List, Dict, Any
from pydantic import BaseModel


class ExtractRequest(BaseModel):
    url: str
    prompt: str

class ExtractResponse(BaseModel):
    data: List[Dict[str, Any]]
    schema_used: Dict[str, Any]