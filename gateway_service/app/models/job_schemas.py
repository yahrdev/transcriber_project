"""
Defines MongoDB job document schemas.
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Union, Literal, List, Optional
from uuid import UUID
from datetime import datetime



class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class JobError(BaseModel):
    code: Optional[str] = None
    message: Optional[str] = None

class JobSourceType(str, Enum):
    file = "file"
    reference = "reference"


class Job(BaseModel):
    job_id: UUID
    client_id: Optional[str] = None
    status: Optional[JobStatus]  = None
    source_type: Optional[JobSourceType]  = None
    source: Optional[str] = None
    file_name: Optional[str] = None
    result_file_path: Optional[str] = None
    error: Optional[JobError] = None
    created_at: Optional[datetime]  = None
    updated_at: Optional[datetime]  = None