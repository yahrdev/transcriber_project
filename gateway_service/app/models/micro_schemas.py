"""
Contains schemas used for inter-service communication.
"""


from pydantic import BaseModel, Field
from enum import Enum
from typing import Union, Literal, List, Optional
from uuid import UUID
from app.models.common import SourceType

class AuthNone(BaseModel):
    method: Literal["none"]

class DownloaderSourceData(BaseModel):
    source_type: SourceType = Field(min_length=1)
    source: str = Field(min_length=1)
    auth: AuthNone

class ConverterSourceData(BaseModel):
    file_path: str = Field(min_length=1)
    target_filename: str = Field(min_length=1)
    source_extension: Optional[str] = Field(min_length=1)
    target_extension: str = Field(min_length=1)

class TranscriberSourceData(BaseModel):
    file_path: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    target_extension: str = "txt"
    language: str = "en"


class MicroserviceError(BaseModel):
    service: str
    status_code: int
    error_code: str
    message: str



class DownloaderResponseData(BaseModel):
    file_path: str  = Field(min_length=1)
    file_name: str  = Field(min_length=1)
    file_extension: str  = Field(min_length=1)

class ConverterResponseData(BaseModel):
    file_path: str  = Field(min_length=1)
    file_name: str  = Field(min_length=1)
    file_extension: str  = Field(min_length=1)

class TranscriberResponseData(BaseModel):
    file_path: str  = Field(min_length=1)

