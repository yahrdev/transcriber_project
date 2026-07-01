"""
handlers.py

Handlers for Flask web UI service errors.
"""

from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound

from app.schemas import Message, MessageSchema
from app.exceptions.errors import STATUS_MAP, ERROR_CODE_MAP, ERROR_DEFINITIONS
from app.exceptions.exceptions import AppError, MicroserviceError
from app.logger.error_logger import log_exception


def handle_request_validation_error(error: ValidationError):
    """Handles validation errors from request data."""

    try:
        errors = []

        for field, messages in error.messages.items():
            for msg in messages:
                errors.append({
                    "field": field,
                    "details": msg
                })

        return get_error_response(
            code="BAD_REQUEST",
            error=error,
            message=errors
        )

    except Exception:
        return get_error_response(
            code="BAD_REQUEST",
            error=error,
            message=str(error)
        )


def handle_not_found_error(error: NotFound):
    """Handles 404 errors."""

    return get_error_response(
        code="NOT_FOUND",
        error=error,
        message=str(error.description)
    )


def handle_app_error(error: AppError):
    """Handles custom application errors."""

    if error.code not in STATUS_MAP:
        raise RuntimeError(
            f"STATUS_MAP is missing HTTP status for code: {error.code}"
        )

    status_code = STATUS_MAP.get(error.code)

    if status_code < 500:
        return make_error_response(
            message=error.message,
            status_code=status_code,
            error=error,
            error_code=error.code
        )

    return get_error_response(
        code="INTERNAL_ERROR",
        error=error
    )


def handle_microservice_error(error: MicroserviceError):
    """
    Handles errors received from downstream microservices.

    For the web UI service, we hide upstream details from the user
    and return a unified internal error response.
    """

    return get_error_response(
        code="INTERNAL_ERROR",
        error=error
    )


def handle_internal_error(error: Exception):
    """Handles all unexpected internal errors."""

    return get_error_response(
        code="INTERNAL_ERROR",
        error=error
    )


def register_error_handlers(app):
    """Registers Flask error handlers."""

    app.register_error_handler(NotFound, handle_not_found_error)
    app.register_error_handler(ValidationError, handle_request_validation_error)
    app.register_error_handler(AppError, handle_app_error)
    app.register_error_handler(MicroserviceError, handle_microservice_error)
    app.register_error_handler(Exception, handle_internal_error)


def get_error_code(error):
    """Maps known exception types or HTTP status codes to internal error codes."""

    for exc_class, code in ERROR_CODE_MAP.items():
        if isinstance(error, exc_class):
            return code

    http_status = getattr(error, "status_code", None)
    if http_status:
        return f"HTTP_{http_status}"

    return type(error).__name__


def make_error_response(
    message,
    status_code,
    error=None,
    error_code=None
):
    """Builds a unified JSON error response and logs the exception."""

    if error_code:
        code = error_code
    else:
        code = getattr(error, "code", None)

    if not isinstance(code, str):
        code = get_error_code(error)

    msg_obj = Message(
        message=message,
        code=code
    )

    msg_json = MessageSchema().dump(msg_obj)

    log_exception(
        error,
        http_status=status_code,
        http_message=message
    )

    return jsonify(msg_json), status_code


def get_error_response(code: str, error=None, message=None):
    """Builds response from predefined error definitions."""

    err_def = ERROR_DEFINITIONS[code]

    return make_error_response(
        message=message or err_def["message"],
        status_code=err_def["status"],
        error=error,
        error_code=code
    )