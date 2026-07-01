"""
Provides media file and MIME type validation utilities.
"""

import subprocess
import magic
from app.exceptions.exceptions import AppError
from typing import Union
import re
from app.exceptions.exceptions import AppError


    
def validate_language(language: str) -> str:
    if language:
        language = language.strip().lower()

        if not re.fullmatch(r"[a-z]{2}", language):
            raise AppError("INVALID_LANGUAGE_FORMAT", value = language)

    return language
    


    