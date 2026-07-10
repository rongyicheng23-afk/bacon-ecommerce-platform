from typing import Any
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: str = "0000"
    info: str = "success"
    data: Any = None
