"""
schemas.py

Pydantic models used in the project
"""

from pydantic import BaseModel, Field
from typing import Union, List, Optional


class SourceData(BaseModel):  
    """
    Main request model used in the /transcribe endpoint.
    Defines file path and optional extension and language data
    """

    file_path: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    target_extension: str = "txt"
    language: str = "uk"


class ResponseData(BaseModel):
    """
    Response model returned after successful transcription.
    Contains the path to saved file.
    """
    file_path: str


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