"""
handlers.py

Handlers for the API errors
"""


from flask import jsonify
from app.api.schemas import Message, MessageSchema
from app.services.error_logger import log_exception
from marshmallow import ValidationError
from app.exceptions.errors import STATUS_MAP, ERROR_CODE_MAP, ERROR_DEFINITIONS
from app.exceptions.exceptions import AppError
from werkzeug.exceptions import NotFound

def handle_request_validation_error(error: ValidationError):

    """400. We detail the error that arises when a user sends incorrect data in JSON"""
    
    try:
        errors = []

        for field, messages in error.messages.items():
            for msg in messages:
                errors.append({
                    "field": field,
                    "details": msg
                })

        return get_error_response("BAD_REQUEST", error=error, message=errors)

    except Exception:
        return get_error_response("BAD_REQUEST", error=error, message=str(error.description))


def handle_not_found_error(error: NotFound):

    """404. We detail the error that arises when the resource was not found"""

    return get_error_response("NOT_FOUND", error=error, message=str(error.description))


def handle_internal_error(error: Exception):

    """We change the format of any exception"""

    return get_error_response("INTERNAL_ERROR", error=error)


def handle_app_error(error: AppError):

    """handler for custom AppError of the app"""

    if error.code not in STATUS_MAP:
        raise RuntimeError(f"STATUS_MAP is missing HTTP status for code: {error.code}")
    
    status_code = STATUS_MAP.get(error.code)
    if status_code < 500:
        return make_error_response(error.message, status_code, error=error) 
    else: 
        return get_error_response("INTERNAL_ERROR", error=error)



def register_error_handlers(app):
    app.register_error_handler(NotFound, handle_not_found_error)
    app.register_error_handler(Exception, handle_internal_error)
    app.register_error_handler(ValidationError, handle_request_validation_error)
    app.register_error_handler(AppError, handle_app_error)

def get_error_code(error):

    """Maps known exception types or HTTP status codes to internal error codes."""

    for exc_class, code in ERROR_CODE_MAP.items():
        if isinstance(error, exc_class):
            return code
    http_status = getattr(error, "status_code", None)
    if http_status:
        return f"HTTP_{http_status}"

def make_error_response(message, status_code, error=None):

    """Build a unified JSON error response and log the original exception with HTTP context."""

    code = getattr(error, "code", None) 
    if not isinstance(code, str):
        code = get_error_code(error)
    msg_obj = Message(message=message, code = code)
    msg_json = MessageSchema().dump(msg_obj)
    log_exception(error, http_status=status_code, http_message=message)
    return jsonify(msg_json), status_code

def get_error_response(code: str, error=None, message=None):

    """Correct messages and statuses of the handled errors"""

    err_def = ERROR_DEFINITIONS[code]
    return make_error_response(
        message=message or err_def["message"],
        status_code=err_def["status"],
        error=error
    )
