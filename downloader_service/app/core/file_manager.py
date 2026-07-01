"""
file_manager.py

The module for processing received files from the endpoint.
"""


import os
import shutil
from pathlib import Path
from typing import Tuple, Union
import uuid
from abc import ABC, abstractmethod
from app.exceptions.exceptions import AppError
import json

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
    def clear_temp_file(self, file_path: str):

        pass

    @abstractmethod  
    def load_json(self) -> dict:
        pass
        



class LocalStorageFileManager(FileManager):

    """
    Concrete implementation of FileManager for saving files to local disk.
    Handles byte content and file copying from existing paths.
    """

    def __init__(self, settings):
        super().__init__(settings)

    
    def get_tmp_dir(self) -> str:
        workdir = self._settings.TEMP_DIR_OUTPUT
        os.makedirs(workdir, exist_ok=True) # create tmp workdir
        return workdir
        
    def create_tmp_file_path(self, file_extension: str, file_name = None) -> Tuple[str, str]:
        workdir = self.get_tmp_dir()
        if file_name is None:
            file_name = f"{uuid.uuid4()}"
        tmp_path = os.path.join(workdir, f"{file_name}.{file_extension}")
        tmp_path = Path(tmp_path).resolve()  # remove .. at the beginning
        tmp_path = tmp_path.as_posix()  # correct / in the result
        return tmp_path, file_name  

        
    
    def save_to_tmp(self, tmp_path: str, source: Union[bytes, str]):

        if not source:
            raise AppError("SOURCE_IS_EMPTY_OR_INVALID")

        if isinstance(source, bytes):
            with open(tmp_path, "wb") as f:
                f.write(source)
        elif isinstance(source, str):
            # A string source is treated as an existing local file path and copied to temp storage.
            if source == tmp_path:
                if not os.path.exists(tmp_path):
                    raise AppError("FILE_NOT_FOUND_PATH", path = tmp_path)
            else:
                if not os.path.exists(source):
                    raise AppError("FILE_NOT_FOUND_PATH", path = source)
                shutil.copy(source, tmp_path)
        else:
            raise AppError("SOURCE_IS_EMPTY_OR_INVALID")
        
    def clear_temp_file(self, file_path: str):
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
       
    def load_json(self) -> dict:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "allowed_extensions.json")
        with open(file_path) as f:
            return json.load(f)
        
    
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