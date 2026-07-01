"""
errors.py

Mappings of error codes to messages and HTTP statuses.
"""

from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError

ERROR_MESSAGES = {
    "FILE_NOT_FOUND_PATH": "The file was not found at the path {path}.",
    "INVALID_FILE_PATH": "Invalid file path {path}. Make sure it includes a valid filename and extension (e.g., .mp3).",
    "UNSUPPORTED_EXTENSION": "Unsupported extension: {value}",
    "TRANSCRIBER_NOT_IMPLEMENTED": "Transcriber for {type} type is not implemented.",
    "INTERNAL_ERROR": "Internal Server Error",
    "SOURCE_IS_EMPTY_OR_INVALID": "Source is empty or invalid", 
    "FILE_MANAGER_NOT_IMPLEMENTED": "File manager for {type} type is not implemented.",
    "TRANSCRIBER_API_ERROR": "Transcription service returned an error: {value}.",
    "TRANSCRIBER_CONNECTION_ERROR": "Cannot connect to transcription service. Error: {value}",
    "TRANSCRIBER_RATE_LIMIT": "Transcription rate limit exceeded.",
    "OPENAI_API_KEY_MISSING": "OpenAI key is empty",
    "INVALID_LANGUAGE_FORMAT": "The language {value} is invalid"
}

STATUS_MAP = {
    "TRANSCRIBER_NOT_IMPLEMENTED": 422,
    "FILE_NOT_FOUND_PATH": 404,
    "INVALID_FILE_PATH": 422,
    "UNSUPPORTED_EXTENSION": 422, 
    "FILE_MANAGER_NOT_IMPLEMENTED": 422,
    "INTERNAL_ERROR": 500,
    "SOURCE_IS_EMPTY_OR_INVALID": 422,
    "BAD_REQUEST": 400,
    "TRANSCRIBER_API_ERROR": 500,          
    "TRANSCRIBER_CONNECTION_ERROR": 500,   
    "TRANSCRIBER_RATE_LIMIT": 429,   
    "OPENAI_API_KEY_MISSING": 500,
    "INVALID_LANGUAGE_FORMAT": 422      
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