"""
models.py

Pydantic models used in the testing of the project
"""

from pydantic import BaseModel, Field
from typing import Literal, Union, List, Optional


class AuthNone(BaseModel):
    method: Literal["none"]

class AuthCookies(BaseModel):
    method: Literal["cookies"] 
    cookies: str = Field(min_length=10)

class AuthLoginPassword(BaseModel):
    method: Literal["login_password"]
    username: str = Field(min_length=2)
    password: str = Field(min_length=2)

class AuthToken(BaseModel):
    method: Literal["token"]
    token: str = Field(min_length=10)

AuthInfo = Union[AuthNone, AuthCookies, AuthLoginPassword, AuthToken]





class SourceData(BaseModel):  
    """
    Main request model used in the /extract endpoint.
    Defines source type, source path or URL, and optional authorization data.
    """
    source_type: str
    source: str
    auth: AuthInfo

class ResponseData(BaseModel):
    """
    Response model returned after successful extraction.
    Contains the path to saved file, original file_name and its file_extension.
    """
    file_path: str
    file_name: str
    file_extension: str

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