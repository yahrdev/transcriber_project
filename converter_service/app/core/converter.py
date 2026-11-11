"""
converter.py

Abstract base class for file converters.

"""

from abc import ABC, abstractmethod
import magic
from pydub import AudioSegment
from tqdm import tqdm
from app.core.file_manager import get_file_manager
import os
from app.exceptions.exceptions import AppError
from app.api.schemas import Output
import app.core.allowed_conversions as ac
from typing import Optional
import shutil



class Converter(ABC):

    def __init__(self, settings, file_manager=None):
        self.file_manager = file_manager or get_file_manager(settings)
        self._settings = settings

    @classmethod
    @abstractmethod
    def supports(cls):

        """List of supported (from, to) extension pairs."""

        pass

    @abstractmethod
    def convert(self, input_path: str, file_name: str, extension_to: str, extension_from: str = None) -> Output:
        """
            Returns:
            Output: Contains path, file_name, and extension of the converted file.
        """
        pass

    def precheck_file(self, path: str, expected_ext: str):

        """ Validations before the conversion."""

        if not os.path.exists(path):
            raise AppError("FILE_NOT_FOUND_PATH", path=path)
        ext = extract_extension(path)
        if ext != expected_ext:
            raise AppError("EXTENSION_MISMATCH", ext=ext, expected=expected_ext)



class ConvertVideoAudio(Converter):

    """Converts video to audio"""

    def __init__(self, settings, file_manager=None):
        super().__init__(settings, file_manager)

    @classmethod
    def supports(cls):
        return ac.Allowed_conversions["video_to_audio"]


    def convert(self, input_path: str, file_name: str, extension_to: str, extension_from: str = None):
        self.precheck_file(path = input_path, expected_ext=extension_from)
        SHOW_PROGRESS = self._settings.DEBUG_PROGRESS

        self.check_mediafile(input_path)
        (output_path, _) = self.file_manager.create_tmp_file_path(extension_to, file_name=file_name)
        try:
            chunk_size = 10_000
            AudioSegment.converter = self.file_manager.get_ffmpeg_path()
            # Use bundled ffmpeg if present; otherwise rely on system ffmpeg

            audio = AudioSegment.from_file(input_path)

        
            total_duration = len(audio)

        
            processed_audio = AudioSegment.empty()

            # For showing progress on backend (for debug only)
            iterator = range(0, total_duration, chunk_size)
            if SHOW_PROGRESS:
                iterator = tqdm(iterator, desc="Convertation", unit="chunk")

            # Process audio in chunks to keep the conversion flow predictable
            # and make debug progress tracking easier.
            for start in iterator:
                end = min(start + chunk_size, total_duration)
                chunk = audio[start:end]  
                processed_audio += chunk  # Cut a part and add to the final audio object

        
            with open(output_path, "wb") as f:
                processed_audio.export(f, format=extension_to)
            if SHOW_PROGRESS:
                print("\n Finished:", output_path)

            return Output(file_path=output_path, file_name=file_name, file_extension=extension_to)
        except Exception:
            self.file_manager.clear_temp_file(file_path = output_path)
            raise
        
    def check_mediafile(self, path: str):

        """check whether the file is audio or video"""

        mime = magic.from_file(path, mime=True)       
        if not (mime.startswith("audio/") or mime.startswith("video/")):
            raise AppError("FILE_WRONG_TYPE", path = path)
        


class CopyAudio(Converter):
    """Copies audio file to converter output without re-encoding."""

    def __init__(self, settings, file_manager=None):
        super().__init__(settings, file_manager)

    @classmethod
    def supports(cls):
        return ac.Allowed_conversions["copy_audio"]


    def convert(self, input_path: str, file_name: str, extension_to: str, extension_from: str = None):
        
        self.precheck_file(path = input_path, expected_ext=extension_from)
        SHOW_PROGRESS = self._settings.DEBUG_PROGRESS

        self.check_mediafile(input_path)
        (output_path, _) = self.file_manager.create_tmp_file_path(extension_to, file_name=file_name)
        shutil.copyfile(input_path, output_path)
        
        if SHOW_PROGRESS:
            print("\n Finished:", output_path)

        return Output(file_path=output_path, file_name=file_name, file_extension=extension_to)
        
    def check_mediafile(self, path: str):

        """check whether the file is audio or video"""

        mime = magic.from_file(path, mime=True)       
        if not (mime.startswith("audio/") or mime.startswith("video/")):
            raise AppError("FILE_WRONG_TYPE", path = path)
        

    

def get_convertator(extension_from: str, extension_to: str, settings) -> Converter:
    from app.core.conversion_registry import ConversionRegistry
    converter_cls = ConversionRegistry.get_converter(extension_from, extension_to)
    if not converter_cls:
        raise AppError("WRONG_CONVERSION", from_ext = extension_from, to_ext = extension_to)
    return converter_cls(settings=settings)



def extract_extension(path: str) -> str:

    """extract extension from the provided path"""

    ext = os.path.splitext(path)[1]
    ext = ext.lstrip(".")
    if ext == "":
        raise AppError("INVALID_FILE_PATH", path = path)
    return ext
