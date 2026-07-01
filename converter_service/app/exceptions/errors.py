"""
errors.py

Mappings of error codes to messages and HTTP statuses.
"""

from werkzeug.exceptions import NotFound
from marshmallow import ValidationError

ERROR_MESSAGES = {
    "FILE_WRONG_TYPE": "The file {path} is not a supported media file.",
    "WRONG_CONVERSION": "No converter for {from_ext} \u2192 {to_ext}.",
    "FILE_NOT_FOUND_PATH": "The file was not found at the path {path}.",
    "INVALID_FILE_PATH": "Invalid file path {path}. Make sure it includes a valid file_name and extension (e.g., .mp4).",
    "EXTENSION_MISMATCH": "Extracted extension from file_path ({ext}) does not equal to the specified '{expected}'.",
    "UNSUPPORTED_EXTENSION": "Unsupported extension: {value}. Supported: {supported}.",
    "FILE_MANAGER_NOT_IMPLEMENTED": "File manager for {type} type is not implemented.",
    "INTERNAL_ERROR": "Internal Server Error",
    "WRONG_TYPE": "Wrong temporary file type. Should be 'input' or 'output'. Current value: {type}"
}

STATUS_MAP = {
    "FILE_WRONG_TYPE": 400,
    "WRONG_CONVERSION": 422,
    "FILE_NOT_FOUND_PATH": 404,
    "INVALID_FILE_PATH": 422,
    "EXTENSION_MISMATCH": 422,
    "UNSUPPORTED_EXTENSION": 422, 
    "FILE_MANAGER_NOT_IMPLEMENTED": 500,
    "INTERNAL_ERROR": 500,
    "WRONG_TYPE": 500
}

ERROR_CODE_MAP = {
    NotFound: "ROUTE_NOT_FOUND",
    ValidationError: "VALIDATION_ERROR",
    Exception: "INTERNAL_ERROR"
}

ERROR_DEFINITIONS = {
    "INTERNAL_ERROR": {
        "status": 500,
        "message": "Internal Server Error"
    },
    "BAD_REQUEST": {
        "status": 400,
        "message": "Bad Request"
    },
    "NOT_FOUND": {
        "status": 404,
        "message": "Not Found"
    }
}