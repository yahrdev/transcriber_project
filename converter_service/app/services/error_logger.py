"""
error_logger.py

Generates JSON logs to be sent to the corresponding service.
"""
import traceback
import uuid
import platform
from datetime import datetime
from flask import request, has_request_context
import json
import os


def log_exception(exc: Exception, func: callable = None, http_status: int = None, http_message: str = None):
    DISABLE_LOGGING = os.getenv("DISABLE_ERROR_LOGGING") == "1"
    if not DISABLE_LOGGING:
        error_dict = get_error_log_dict(exc, func, http_status, http_message)

        # for displaying in the terminal
        print("LOGGED ERROR:")   
        print(json.dumps(error_dict, indent=2, ensure_ascii=False))


def get_error_log_dict(exc: Exception, func: callable = None, http_status: int = None, http_message: str = None) -> dict:
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
    if has_request_context():
        try:
            json_data = None
            try:
                json_data = request.get_json(silent=True)
            except Exception as e:
                json_data = f"<< Failed to parse JSON: {e} >>"

            log_data["request"] = {
                "method": request.method,
                "url": request.url,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent"),
                "json": json_data
            }

        except Exception as e:
            log_data["request"] = f"<< Failed to collect request data: {e} >>"

    return log_data




