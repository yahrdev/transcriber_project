"""
extractor.py

Module responsible for downloading video files from external URLs
and saving them to a temporary local directory for further processing
by other microservices
"""

from typing import Union
from abc import ABC, abstractmethod
from app.core.file_manager import get_file_manager
from app.core.schemas import SourceType, ResponseData, AuthInfo
from app.exceptions.exceptions import AppError
from app.utils.validators import is_url
from app.utils.extensions import get_extension_from_path, get_extension_from_url, is_supported_extension
from app.utils.network import get_request_content

class FileExtractor(ABC):
    """
    Abstract base class for extracting files from different source types
    """

    def __init__(self, settings, file_manager=None):
        self.file_manager = file_manager or get_file_manager(settings)
        self._settings = settings

    
    def extract(self, auth: AuthInfo, source: str) -> ResponseData:
        """
        Extracts a file from the given source, validates it, downloads content,
        and saves it to temporary storage.

        Auth metadata is reserved for extractors that need authenticated access
        remote sources. Current implementations may ignore it.

        Returns:
            ResponseData: Contains file_path, file_name, and file_extension of the saved file.
        """
        
        self.validate_source(source)

        self.check_source_type(source)

        file_extension = self.get_extension(source)

        supported_exts = self.file_manager.load_json()
        if is_supported_extension(file_extension, supported_exts):

            # Normalize all supported sources into a temporary local file
            # so downstream services always work with the same file contract.

            tmp_path, file_name = self.file_manager.create_tmp_file_path(file_extension)
            try:
                request_content = self.get_source_content(source)
                self.file_manager.save_to_tmp(tmp_path, request_content)
                return ResponseData(file_path = tmp_path,
                                    file_name=file_name,
                                    file_extension=file_extension)
            except Exception:
                self.file_manager.clear_temp_file(file_path = tmp_path)
                raise
        
        else:
            raise AppError("UNSUPPORTED_EXTENSION", value = file_extension)
        
    @abstractmethod
    def check_source_type(self, source: str) -> None:
        pass

    @abstractmethod
    def get_extension(self, source: str) -> str:
        pass

    @abstractmethod
    def get_source_content(self, source: str) -> Union[str, bytes]:
        pass
    
    def validate_source(self, source: str):
        if not source or not isinstance(source, str):
            raise AppError("SOURCE_IS_EMPTY_OR_INVALID")
        



class FileExtractorURL(FileExtractor):  

    """
    Concrete implementation for extracting files from HTTP/HTTPS URLs.
    Checks URL validity, extracts extension from URL, and downloads file content.
    """
      
    
    def check_source_type(self, source: str)  -> None:
        if not is_url(source):
            raise AppError("NOT_URL", value=source)

    
    def get_extension(self, source: str) -> str:
        return get_extension_from_url(source)

    
    def get_source_content(self, source: str) -> Union[str, bytes]:
        return get_request_content(source)

    
    

    
class FileExtractorPath(FileExtractor):

    """
    Concrete implementation for handling already existing local file paths.
    Extracts extension and returns path as content (no downloading).
    """

    
    def check_source_type(self, source: str)  -> None:
        """Path sources do not require extra type validation at extractor level."""
        pass

    
    def get_extension(self, source: str) -> str:
        return get_extension_from_path(source)

    
    def get_source_content(self, source: str) -> Union[str, bytes]:
        # For local paths we do not download content; the file manager will copy
        # the source file into the service temporary directory.
        return source


# ──── Factory ─────────────────────────────────────────────

extractor_registry = {
    SourceType.url: FileExtractorURL, 
    SourceType.path: FileExtractorPath
}

def get_extractor(source_type, settings) -> FileExtractor:
    extractor_class = extractor_registry.get(source_type)
    if not extractor_class:
        raise AppError("EXTRACTOR_NOT_IMPLEMENTED", type=source_type)
    return extractor_class(settings)







    


    



