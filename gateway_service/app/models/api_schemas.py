"""
Contains API request and response schemas.
"""

from pydantic import BaseModel, Field
from typing import Union, Literal, List, Optional
from uuid import UUID
from app.models.common import SourceType
from app.models.job_schemas import JobStatus


class SourceData(BaseModel):
    client_id: str
    source_type: SourceType  = Field(min_length=1)
    source: str  = Field(min_length=1)
    language: str  = Field(min_length=2)

class ResponseDataModel(BaseModel):
    result_url: str

class ResponseStatusModel(BaseModel):
    job_id: UUID
    status: JobStatus

class PostResponseData(BaseModel):
    job_id: UUID
    data: Optional[ResponseDataModel]


