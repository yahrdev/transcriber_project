"""
extensions.py

Utility functions for extracting  extensions from files.
"""

import os
from app.exceptions.exceptions import AppError
from pathlib import Path


def extract_extension(filenamewithext: str) -> str:
    """
    Extracts the file extension from a given path or filename.

    Raises:
        AppError: If no extension is found.
    """
    ext = Path(filenamewithext).suffix.lstrip(".")
    if ext == "":
        raise AppError("INVALID_FILE_EXTENSION", file= filenamewithext)
    return ext



