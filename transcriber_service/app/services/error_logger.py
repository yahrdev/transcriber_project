"""
error_logger.py

Generates JSON logs to be sent to the corresponding service.
"""
import traceback
import uuid
import platform
from datetime import datetime
from fastapi import Request
import json
import os


def log_exception(exc: Exception, func: callable = None, http_status: int = None, http_message: str = None, request=None):
    DISABLE_LOGGING = os.getenv("DISABLE_ERROR_LOGGING") == "1"
    if not DISABLE_LOGGING:
        error_dict = get_error_log_dict(exc, func, http_status, http_message, request)

        # for displaying in the terminal
        print("LOGGED ERROR:")   
        print(json.dumps(error_dict, indent=2, ensure_ascii=False))


def get_error_log_dict(exc: Exception, func: callable = None, http_status: int = None, http_message: str = None, request = None) -> dict:
    
    # Creates a structured error log that can later be sent to a logging service
    # or stored in a database (for example MongoDB).
    # Traceback is truncated to avoid extremely large logs.
    
    error_id = str(uuid.uuid4())

    # Get and truncate the traceback
    full_traceback = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    short_traceback = full_traceback[-3000:] if len(full_traceback) > 3000 else full_traceback

    # Get info about the original error 
    origin_info = {}
    tb = traceback.extract_tb(exc.__traceback__)
    if tb:
        origin_frame = tb[-1]
        origin_info = {
            "origin_file": origin_frame.filename,
            "origin_function": origin_frame.name,
            "origin_line": origin_frame.lineno
        }

    # The location where log_exception was called
    log_context = {}
    if func:
        log_context["module"] = func.__module__
        log_context["function"] = func.__name__
        if hasattr(func, '__self__') and hasattr(func.__self__, '__class__'):
            log_context["class"] = func.__self__.__class__.__name__

    # Create a JSON structure
    log_data = {
        "id": error_id,
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "traceback": short_traceback,
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
        },
        **origin_info,
        **log_context,
    }

    # HTTP part
    if http_status:
        log_data["http_status"] = http_status
    if http_message:
        log_data["http_error_message"] = http_message

    # Data about the HTTP request (if any)
    if request:
        try:
            log_data["request"] = {
                "method": request.method,
                "url": str(request.url),
                "client_host": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent"),
                "json": "<< not available in sync >>"
            }
        #TODO: add "json" for user's request as in the main microservice
        except Exception as e:
            log_data["request"] = f"<< Failed to collect request data: {e} >>"

    return log_data



