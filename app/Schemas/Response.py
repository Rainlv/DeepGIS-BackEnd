from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class BaseResponse(BaseModel):
    code: int = 0
    message: str = ''
    result: Optional[List[Dict[str, Any]]] = []
