"""
file_manager.py

The module for processing received files from the endpoint.
"""


import os
import glob
import shutil
from pathlib import Path
from typing import Tuple, Union, Optional
import uuid
from abc import ABC, abstractmethod
from app.exceptions.exceptions import AppError
import json
import platform
from app.services.error_logger import log_exception


class FileManager(ABC):

    """Abstract base class for file manager implementations."""

    def __init__(self, settings):
        self._settings = settings


    @abstractmethod
    def get_tmp_dir(self) -> str:
        pass
        
    @abstractmethod
    def create_tmp_file_path(self, file_extension: str, file_name = None) -> Tuple[str, str]:
        """
        Generates a temporary file path with the given extension and optional file_name.
        """
        pass
        
    @abstractmethod    
    def save_to_tmp(self, tmp_path: str, source: Union[bytes, str]):
        """
        Saves a file (as bytes or from another local path) to the temporary path.
        """
        pass

    @abstractmethod
    def get_ffmpeg_path(self) -> str:

        """Additional exe files for the conversions"""

        pass

    @abstractmethod
    def clear_temp_folders(self, filename: str):

        """Clear temporary folders after processing."""

        pass

        
class LocalStorageFileManager(FileManager):

    """
    Concrete implementation of FileManager for saving files to local disk.
    Handles byte content and file copying from existing paths.
    """

    def __init__(self, settings):
        super().__init__(settings)

    
    def get_tmp_dir(self) -> str:
        workdir = self._settings.UploadedFilesDir
        os.makedirs(workdir, exist_ok=True) # create tmp workdir
        return workdir
        
    def create_tmp_file_path(self, file_extension: str = None, file_name = None) -> Tuple[str, str]:
        workdir = self.get_tmp_dir()
        if file_name is None:
            file_name = f"{uuid.uuid4()}"
        tmp_path = os.path.join(workdir, f"{file_name}.{file_extension}")
        tmp_path = Path(tmp_path).resolve()  # remove .. at the beginning
        tmp_path = tmp_path.as_posix()  # correct / in the result
        return tmp_path, file_name  
    
  
    
    def save_to_tmp(self, tmp_path: str, source: bytes):

        if not source:
            raise AppError("SOURCE_IS_EMPTY_OR_INVALID")

        if isinstance(source, bytes):
            with open(tmp_path, "wb") as f:
                f.write(source)
        else:
            raise AppError("SOURCE_IS_EMPTY_OR_INVALID")
        

        
    def get_ffmpeg_path(self) -> str:
        ffmpeg_binary = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
        custom_path = os.path.join(self._settings.TOOLS_FOLDER, ffmpeg_binary)

        if os.path.exists(custom_path):
            return custom_path
        else:
            return ffmpeg_binary  # use system ffmpeg
        

    def _delete_files_by_base_name(self, folder: str, base_name: str) -> None:
        
        try:
            pattern = os.path.join(folder, f"{base_name}.*")

            for file_path in glob.glob(pattern):
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            log_exception(e)    


    def clear_temp_folders(self, filename: str):

        """
        Removes temporary files created during media processing.

        Cleanup is performed using the generated base filename
        associated with the current job.
        """

        # TODO: current implementation uses glob-based cleanup by base filename.
        # Works for single-file jobs, but should be replaced with job_id-based file isolation
        # (e.g., /shared/jobs/<job_id>/...) to support concurrency and scaling.

        self._delete_files_by_base_name(self._settings.DOWNLOADER_OUTPUT_DIR, filename)
        self._delete_files_by_base_name(self._settings.CONVERTER_OUTPUT_DIR, filename)
        self._delete_files_by_base_name(self._settings.UPLOADED_FILES_DIR, filename)

    



        
    
file_manager_registry = {
    "local": LocalStorageFileManager
}


def get_file_manager(settings) -> FileManager:

    """
    Factory function to retrieve the appropriate file manager implementation based on settings.
    """

    manager_class = file_manager_registry.get(settings.STORAGE_TYPE)
    if not manager_class:
        raise AppError("FILE_MANAGER_NOT_IMPLEMENTED", type=settings.STORAGE_TYPE)
    return manager_class(settings)

