"""
errors.py

Mappings of error codes to messages and HTTP statuses.
"""

from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError


ERROR_MESSAGES = {
    "INTERNAL_ERROR": "Internal Server Error",
    "SOURCE_IS_EMPTY_OR_INVALID": "Source is empty or invalid", 
    "FILE_MANAGER_NOT_IMPLEMENTED": "File manager for {type} type is not implemented.",
    "UNKNOWN_TYPE": "The uploaded file has unknown type",
    "FILE_CORRUPTED": "Uploaded file is corrupted or cannot be processed as media",
    "JOB_NOT_FOUND": "The job {job_id} was not found in the database",
    "CAN_NOT_CREATE_DOCUMENT": "The job can not be created",
    "INVALID_LANGUAGE_FORMAT": "The language {value} is invalid",
    "FILE_WRONG_TYPE": "The file should be video or audio type",
    "INVALID_FILE_EXTENSION": "Invalid file extension {file}. Make sure it includes a valid extension (e.g., .mp3).",
    "REQUEST_SERIALIZATION_ERROR": "Invalid request to the microservice {value}",
    "NOT_FINISHED": "The process has not been finished yet",
    "JOB_FAILED": "The process was failed",
    "BIG_FILE": "The file is too large"
}

STATUS_MAP = {
    "FILE_MANAGER_NOT_IMPLEMENTED": 500,
    "INTERNAL_ERROR": 500,
    "SOURCE_IS_EMPTY_OR_INVALID": 422,
    "BAD_REQUEST": 400,
    "UNKNOWN_TYPE": 500,
    "FILE_CORRUPTED": 422,
    "JOB_NOT_FOUND": 500,
    "CAN_NOT_CREATE_DOCUMENT": 500,
    "INVALID_LANGUAGE_FORMAT": 422,
    "FILE_WRONG_TYPE": 422,
    "INVALID_FILE_EXTENSION": 422,
    "REQUEST_SERIALIZATION_ERROR": 500,
    "NOT_FINISHED": 409,
    "JOB_FAILED": 409,
    "BIG_FILE": 413

}


ERROR_CODE_MAP = {
    ValidationError: "VALIDATION_ERROR",
    Exception: "INTERNAL_ERROR",
    RequestValidationError: "VALIDATION_ERROR"
}

ERROR_DEFINITIONS = {
    "INTERNAL_ERROR": {
        "status": 500,
        "message": "Internal Server Error"
    },
    "BAD_REQUEST": {
        "status": 400,
        "message": "Bad Request"
    }
}