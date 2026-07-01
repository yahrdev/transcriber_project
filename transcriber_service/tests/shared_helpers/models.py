"""
models.py

Pydantic models used in the testing of the project
"""

from pydantic import BaseModel
from typing import Union, List, Optional


class SourceData(BaseModel):  
    """
    Main request model used in the /extract endpoint.
    Defines file path and optional extension and language data
    """

    file_path: Optional[str] = None
    file_name: Optional[str] = None
    target_extension: Optional[str] = None
    language: Optional[str] = None


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