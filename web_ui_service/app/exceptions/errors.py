"""
errors.py

Mappings of error codes to messages and HTTP statuses.
"""

from pydantic import ValidationError
from werkzeug.exceptions import NotFound


ERROR_MESSAGES = {
    "INTERNAL_ERROR": "Internal Server Error"
}

STATUS_MAP = {
    "INTERNAL_ERROR": 500,
    "BAD_REQUEST": 400,

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