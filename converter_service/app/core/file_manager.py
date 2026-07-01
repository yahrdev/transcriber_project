import os
import shutil
from typing import Tuple
import uuid
from abc import ABC, abstractmethod
import platform
from app.exceptions.exceptions import AppError


class FileManager(ABC):

    def __init__(self, settings):
        self._settings = settings

    @abstractmethod
    def get_tmp_dir(self) -> str:

        """Get or create a temporary directory."""

        pass
        
    @abstractmethod
    def create_tmp_file_path(self, extension: str,  file_name = None) -> Tuple[str, str]:
        """
        Returns:
            Tuple[tmp_path, file_name (without extension)]
        """
        pass

    @abstractmethod
    def clear_temp_file(self, file_path: str):

        pass


    @abstractmethod
    def get_ffmpeg_path(self) -> str:

        """Additional exe files for the conversions"""

        pass


class LocalStorageFileManager(FileManager):

    """
    The class for managing files on local storage (e.g., D:/).
    """

    def __init__(self, settings):
        super().__init__(settings)

    def get_tmp_dir(self) -> str:
        workdir = self._settings.TEMP_DIR_OUTPUT
        os.makedirs(workdir, exist_ok=True) #create workdir
        return workdir
        
    def create_tmp_file_path(self, extension: str, file_name = None) -> Tuple[str, str]:
        """
        Returns:
            Tuple[tmp_path, file_name (without extension)]
        """
        workdir = self.get_tmp_dir()
        if file_name is None:
            file_name = f"{uuid.uuid4()}"
        tmp_path = os.path.join(workdir, f"{file_name}.{extension}")
        return tmp_path, file_name  
    
    def clear_temp_file(self, file_path: str):
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


    def get_ffmpeg_path(self) -> str:
        ffmpeg_binary = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
        custom_path = os.path.join(self._settings.TOOLS_FOLDER, ffmpeg_binary)

        if os.path.exists(custom_path):
            return custom_path
        else:
            return ffmpeg_binary  # use system ffmpeg
    

file_manager_registry = {
    "local": LocalStorageFileManager
}

def get_file_manager(settings) -> FileManager:
    manager_class = file_manager_registry.get(settings.STORAGE_TYPE)
    if not manager_class:
        raise AppError("FILE_MANAGER_NOT_IMPLEMENTED", type=settings.STORAGE_TYPE)
    return manager_class(settings)