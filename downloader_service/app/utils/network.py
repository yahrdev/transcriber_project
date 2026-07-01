"""
network.py

Utility for downloading binary content from external URLs over HTTP.
"""

import requests
from typing import Optional
from app.exceptions.exceptions import AppError


def get_request_content(url) -> Optional[bytes]:
    """
    Sends an HTTP GET request to the given URL and returns the response content.
    """
    
    response = requests.get(url)
    response_content = response.content
    if (not response_content) or (response.status_code != 200):
        raise AppError("URL_UNREACHABLE", url=url)
    return response_content