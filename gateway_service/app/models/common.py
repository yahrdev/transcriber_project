"""
Contains shared reusable Pydantic models.
"""

from enum import Enum
from pydantic import BaseModel
from typing import Union, List, Optional


class SourceType(str, Enum):
    url = "url"
    file = "path"




class ValidationErrorDetail(BaseModel):  
    """
    Used for returning detailed validation errors in a structured format.
    """
    field: str
    details: str


class Message(BaseModel):    
    """
    Standard response message for both simple errors and detailed validation messages.
    """
    message: Union[str, List[ValidationErrorDetail]]
    code: Optional[str]