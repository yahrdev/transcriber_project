"""
Contains API request and response schemas.
"""

from pydantic import BaseModel
from typing import Union, List, Optional
from uuid import UUID




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


class ResponseDataModel(BaseModel):
    result_url: str


class PostResponseData(BaseModel):
    job_id: UUID
    data: Optional[ResponseDataModel]


