"""
handlers.py

Centralized error handlers and helpers for formatting error responses in the FastAPI app.
"""


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.schemas import Message
from app.services.error_logger import log_exception
from pydantic import ValidationError
from app.exceptions.errors import STATUS_MAP, ERROR_CODE_MAP, ERROR_DEFINITIONS
from app.exceptions.exceptions import AppError
from fastapi.exceptions import RequestValidationError

def handle_request_validation_error(request: Request, error: RequestValidationError):
    """
    Handles the error that arises when a user sends incorrect data in JSON
    """
    try:
        """
            Example: {'type': 'json_invalid', 'loc': ('body', 22), 
            'msg': 'JSON decode error', 'input': {}, 'ctx': {'error': 'Invalid \\escape'}}
        """

        errors = []
        for err in error.errors():
            loc = err.get("loc", [])
            field = ''
            if loc:
                last = loc[-1]
                if isinstance(last, str):
                   field = last
                else:
                   field = "request body"

            msg = err.get("msg", "") or "Validation error"
            hint = (err.get("ctx") or {}).get("error", "")
            details = f"{msg}: {hint}".rstrip(": ").strip() 
            #rstrip  deletes ": " if it is in the end
            #strip deletes extra spaces
            errors.append({"field": field, "details": details})
            
        
        return make_error_response(
            message=errors,
            status_code=STATUS_MAP["BAD_REQUEST"],
            error=error,
            request=request,
            error_code="BAD_REQUEST"
        ) 

    except Exception:
        return generate_error_response("INTERNAL_ERROR", error=error, request = request)



def handle_internal_error(request: Request, error):

    """Handles unexpected internal exceptions and returns them in a unified format."""
    return generate_error_response("INTERNAL_ERROR", error=error, request = request)


def handle_app_error(request: Request, error):

    """Handler for custom AppError of the app"""

    if error.code not in STATUS_MAP:
        raise RuntimeError(f"STATUS_MAP is missing HTTP status for code: {error.code}")
       
    status_code = STATUS_MAP.get(error.code)
    if status_code < 500:
        return make_error_response(error.message, status_code, error=error, request = request) 
    else: 
        return generate_error_response("INTERNAL_ERROR", error=error, request = request)



def register_error_handlers(app: FastAPI):

    """Registers all custom exception handlers to the FastAPI app instance."""

    
    app.add_exception_handler(ValidationError, handle_request_validation_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(Exception, handle_internal_error)
    app.add_exception_handler(AppError, handle_app_error)

def get_error_code(error):

    """Maps known exception types or HTTP status codes to internal error codes."""

    for exc_class, code in ERROR_CODE_MAP.items():
        if isinstance(error, exc_class):
            return code
    http_status = getattr(error, "status_code", None)
    if http_status:
        return f"HTTP_{http_status}"

def make_error_response(message, status_code,  request: Request, error=None, error_code = None):

    """
    Builds a structured JSON error response using FastAPI's JSONResponse.
    Logs the exception and returns appropriate message and code.
    """
    if error_code:
        code = error_code
    else:
        code = getattr(error, "code", None) # If the error has no 'code' attribute, returns None
    if not isinstance(code, str):
        code = get_error_code(error)
    msg_json = Message(message=message, code = code).model_dump()
    log_exception(error, http_status=status_code, http_message=message, request=request)
    return JSONResponse(
        status_code=status_code,
        content=msg_json,
    )

def generate_error_response(code: str, request:Request, error=None, message=None):

    """
    Constructs error response using predefined error definitions from ERROR_DEFINITIONS.
    Used in custom error handlers to unify format.
    """

    err_def = ERROR_DEFINITIONS[code]
    return make_error_response(
        message=message or err_def["message"],
        status_code=err_def["status"],
        error=error,
        request=request, 
        error_code = code
    )

    
