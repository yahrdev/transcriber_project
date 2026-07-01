"""
file_manager.py

The module for processing received files from the endpoint.
"""


import os
import shutil
from pathlib import Path
from typing import Tuple, Union, Optional, List
import uuid
from abc import ABC, abstractmethod
from app.services.error_logger import  log_exception
from app.exceptions.exceptions import AppError
import json

class FileManager(ABC):

    """Abstract base class for file manager implementations."""

    def __init__(self, settings):
        self._settings = settings


    @abstractmethod
    def get_tmp_dir(self, type: Optional[str] = None, subfolder: Optional[str] = None) -> str:

        """Get or create a temporary directory."""

        pass
        
    @abstractmethod
    def create_tmp_file_path(self, extension: str, type: Optional[str] = None, filename: Optional[str] = None,  subfolder: Optional[str] = None) -> Tuple[str, str]:
        """
        Generates a temporary file path with the given extension and optional filename.
        """
        pass
        
    @abstractmethod    
    def save_to_tmp(self, tmp_path: str, source: Union[bytes, str], rewrite = True):
        """
        Saves a file (as bytes or from another local path) to the temporary path.
        """
        pass

    @abstractmethod
    def clear_temp_folders(self, subfolder: Optional[List[str]] = None):

        """Clear temporary folders after processing."""

        pass

    @abstractmethod
    def clear_temp_file(self, file_path: str):

        pass

    @abstractmethod  
    def load_json(self) -> dict:
        """
        Loads a JSON file containing allowed file extensions.
        """
        pass
        



class LocalStorageFileManager(FileManager):

    """
    Concrete implementation of FileManager for saving files to local disk.
    Handles byte content and file copying from existing paths.
    """

    def __init__(self, settings):
        super().__init__(settings)

    
    def get_tmp_dir(self, type: Optional[str] = None, subfolder: Optional[str] = None) -> str:
        workdir = self._settings.TEMP_DIR_OUTPUT
        if type == 'chunk':
            workdir = self._settings.CHUNKS
        
        if subfolder:
            workdir = os.path.join(workdir, subfolder)

        os.makedirs(workdir, exist_ok=True) # create tmp workdir
        return workdir
    
    
 
    def create_tmp_file_path(self, extension: str, type: Optional[str] = None, filename: Optional[str] = None,  subfolder: Optional[str] = None) -> Tuple[str, str]:
        
        # Returns both:
        # - absolute path where the temporary file should be stored
        # - generated filename (useful for returning it in API responses)

        workdir = self.get_tmp_dir(type, subfolder)
        if not filename:
            filename = f"{uuid.uuid4()}"
        tmp_path = os.path.join(workdir, f"{filename}.{extension}")
        tmp_path = Path(tmp_path).resolve()  # remove .. at the beginning
        tmp_path = tmp_path.as_posix()  # correct / in the result
        return tmp_path, filename  

        

    def save_to_tmp(self, tmp_path: str, source: Union[str, List[str], bytes], rewrite = True):

        if not source:
            raise AppError("SOURCE_IS_EMPTY_OR_INVALID")
        if rewrite:
            openmode = "w"
        else:
            openmode = "x"
        if isinstance(source, bytes):
            with open(tmp_path, openmode + "b") as f:
                f.write(source)
        elif isinstance(source, str):
            with open(tmp_path, openmode, encoding="utf-8") as f:
                f.write(source)
        elif isinstance(source, list) and all(isinstance(text, str) for text in source):
            with open(tmp_path, openmode, encoding="utf-8") as f:
                f.write("\n".join(source))
        else:
            raise AppError("SOURCE_IS_EMPTY_OR_INVALID")
        

    def clear_temp_folders(self, subfolder: Optional[str] = None):
        try:
            folder_name = self._settings.CHUNKS
            if subfolder:
                folder_name = os.path.join(self._settings.CHUNKS, subfolder)
            if os.path.isdir(folder_name):
                for filename in os.listdir(folder_name):
                    try:
                        filepath = os.path.join(folder_name, filename)
                        if os.path.isfile(filepath) or os.path.islink(filepath):  #if it is a file or a symlink
                            os.remove(filepath)
                        elif os.path.isdir(filepath):  #if it is a directory
                            shutil.rmtree(filepath)
                    except Exception as e:
                        log_exception(e)
                        
        except Exception as e:
            log_exception(e)


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