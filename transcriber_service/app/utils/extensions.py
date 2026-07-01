"""
extensions.py

Utility functions for extracting and validating file extensions from file paths.
"""

import os
from app.exceptions.exceptions import AppError


def extract_extension(path: str) -> str:
    """
    Extracts the file extension from a given path or filename.

    Raises:
        AppError: If no extension is found.
    """
    
    ext = os.path.splitext(path)[1]
    ext = ext.lstrip(".")
    if ext == "":
        raise AppError("INVALID_FILE_PATH", path= path)
    return ext


def get_extension_from_path(filepath: str) -> str:
    """
    Extracts the file extension from a local file path.
    """

    return extract_extension(filepath)

def is_supported_extension(ext: str, supported_exts: dict) -> bool:
    """
    Checks whether the given extension is among the supported ones.
    """

    for ext_key in supported_exts:
        for e in supported_exts[ext_key]:
            if ext.lower() == e.lower():
                return True
    return False

