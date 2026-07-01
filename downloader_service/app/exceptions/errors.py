"""
errors.py

Mappings of error codes to messages and HTTP statuses.
"""

from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError

ERROR_MESSAGES = {
    "EXTRACTOR_NOT_IMPLEMENTED": "No extractor for source_type {value}.",
    "FILE_NOT_FOUND_PATH": "The file was not found at the path {path}.",
    "INVALID_FILE_PATH": "Invalid file path {path}. Make sure it includes a valid filename and extension (e.g., .mp4).",
    "UNSUPPORTED_EXTENSION": "Unsupported extension: {value}",
    "FILE_MANAGER_NOT_IMPLEMENTED": "File manager for {type} type is not implemented.",
    "INTERNAL_ERROR": "Internal Server Error",
    "NOT_URL": "The source {value} is not a url",
    "SOURCE_IS_EMPTY_OR_INVALID": "Source is empty or invalid",
    "URL_UNREACHABLE": "Could not retrieve data from the URL: {url}"
}

STATUS_MAP = {
    "EXTRACTOR_NOT_IMPLEMENTED": 422,
    "FILE_NOT_FOUND_PATH": 404,
    "INVALID_FILE_PATH": 422,
    "EXTENSION_MISMATCH": 422,
    "UNSUPPORTED_EXTENSION": 422, 
    "FILE_MANAGER_NOT_IMPLEMENTED": 500,
    "INTERNAL_ERROR": 500,
    "WRONG_TYPE": 500, 
    "NOT_URL": 422,
    "SOURCE_IS_EMPTY_OR_INVALID": 422,
    "URL_UNREACHABLE": 404, 
    "BAD_REQUEST": 400
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