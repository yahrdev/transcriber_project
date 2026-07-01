"""
Contains API request and response schemas.
"""

from pydantic import BaseModel
from typing import Union, List, Optional
from uuid import UUID


class SourceData(BaseModel):
    client_id: str
    source_type: str
    source: str
    language: str

class ResponseDataModel(BaseModel):
    result_url: str

class PostResponseData(BaseModel):
    job_id: UUID
    data: Optional[ResponseDataModel]

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


class ResponseStatusModel(BaseModel):
    job_id: UUID
    status: str


