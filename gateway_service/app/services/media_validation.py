"""
Provides media file and MIME type validation utilities.
"""

import subprocess
import magic
from app.exceptions.exceptions import AppError
from typing import Union
import re
from app.exceptions.exceptions import AppError



def validate_media_mime(content: Union[bytes, str]):

    """
    Validates that the provided content belongs to a supported
    audio or video media type.

    Supports validation from either raw bytes or a local file path.
    """
    if isinstance(content, bytes):
        mime = magic.from_buffer(content, mime=True)
    elif isinstance(content,str):
        mime = magic.from_file(content, mime=True)
    else:
        raise AppError("UNKNOWN_TYPE")

         
    if not (mime.startswith("audio/") or mime.startswith("video/")):
        raise AppError("FILE_WRONG_TYPE")
    

def validate_media_file (path: str):

    """
    Verifies that the media file can be successfully decoded.

    Files that cannot be processed by ffmpeg are treated
    as corrupted media.
    """

    result = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    if result.returncode != 0:
        raise AppError("FILE_CORRUPTED")
    
    
def validate_language(language: str) -> str:
    if language:
        language = language.strip().lower()

        if not re.fullmatch(r"[a-z]{2}", language):
            raise AppError("INVALID_LANGUAGE_FORMAT", value = language)

    return language
    


    