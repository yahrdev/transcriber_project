"""
transcriber.py

Abstract base class for file transcriptions.

"""

from abc import ABC, abstractmethod
from pydub import AudioSegment
import math
from app.core.file_manager import get_file_manager
import os
from app.exceptions.exceptions import AppError
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from app.core.schemas import ResponseData
from app.utils.extensions import is_supported_extension, get_extension_from_path
import uuid
from app.services.media_validation import validate_language


class Transcriber(ABC):

    def __init__(self, settings, file_manager=None):
        self.file_manager = file_manager or get_file_manager(settings)
        self._settings = settings

    def transcribe(self, audio_file_path: str, audio_file_name: str, target_extension = "txt", language="uk", chunk_duration=60) -> ResponseData:

        """
        Returns:
            ResponseData: Path to the generated transcription file.
        """

        if not target_extension:
            target_extension = "txt"
        if not language:
            language="en"
        if not chunk_duration:
            chunk_duration = 60

        language = validate_language(language)

        # Audio is processed in chunks to avoid memory issues with long files
        # and to allow large recordings to be transcribed sequentially.
        # Each chunk is sent to the transcription model separately.

        if not os.path.exists(audio_file_path):
            raise AppError("FILE_NOT_FOUND_PATH", path=audio_file_path)

        supported_exts = self.file_manager.load_json()
        current_extension = get_extension_from_path(audio_file_path)
        if not is_supported_extension(current_extension, supported_exts):
            raise AppError("UNSUPPORTED_EXTENSION", value = current_extension)


        client = self.get_client()
        audio = AudioSegment.from_file(audio_file_path, format=current_extension)
        duration = int(audio.duration_seconds)
        total_chunks = math.ceil(duration / chunk_duration)

        transcript = []  
        subfolder_name = f"{uuid.uuid4()}"
        try:
            tmp_path = ""
            for i in range(total_chunks):
                start_time_chunk = i * chunk_duration
                chunk = audio[start_time_chunk * 1000:(start_time_chunk + chunk_duration) * 1000]
                
                
                chunk_path, filename = self.file_manager.create_tmp_file_path(current_extension, 
                                                                            type='chunk',
                                                                            filename=f"temp_chunk_{i}", 
                                                                            subfolder = subfolder_name
                                                                            )
                chunk.export(chunk_path, format=current_extension, parameters=["-ar", "16000", "-ac", "1"])
                # Normalize chunk audio before transcription:
                # 16 kHz mono is used to keep input format consistent for the API.

                with open(chunk_path, "rb") as f:  

                    transcript_text = self.get_transcribed_part(f, client, language)
                    transcript.append(transcript_text)

            tmp_path, filename = self.file_manager.create_tmp_file_path(target_extension, filename=audio_file_name)
            # Save to file
            self.file_manager.save_to_tmp(tmp_path, transcript)
            return ResponseData(file_path = tmp_path)
        except:
            if tmp_path:
                self.file_manager.clear_temp_file(file_path = tmp_path)
                raise
        finally:
            self.file_manager.clear_temp_folders(subfolder=subfolder_name)
            # Always remove chunk files even if transcription fails.
        
    
    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def get_transcribed_part(self, f, client, language):
        pass




class TranscribeByAPI(Transcriber):

    """Transcribes audio"""


    def get_client(self):  
        if not self._settings.OPEN_AI_KEY:
            raise AppError("OPENAI_API_KEY_MISSING")   
        return OpenAI(api_key=self._settings.OPEN_AI_KEY)

    def get_transcribed_part(self, f, client, language):
        try:
            response = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=f,
                            language=language
                        )
            return response.text
        except APIError as e:
            raise AppError("TRANSCRIBER_API_ERROR", value = str(e))

        except APIConnectionError as e:
            raise AppError("TRANSCRIBER_CONNECTION_ERROR", value = str(e))

        except RateLimitError:
            raise AppError("TRANSCRIBER_RATE_LIMIT")

    

class MockTranscribeByAPI(Transcriber):

    """Transcribes audio"""


    def get_client(self):     
        return "Mock Transcribation"

    def get_transcribed_part(self, f, client, language):
        return "Mock Transcribation text"




transcriber_registry = {
    "api": TranscribeByAPI,
    "test_api": MockTranscribeByAPI
}


def get_transcriber(settings) -> Transcriber:
    manager_class = transcriber_registry.get(settings.TRANSCRIBER_TYPE)
    if not manager_class:
        raise AppError("TRANSCRIBER_NOT_IMPLEMENTED", type=settings.TRANSCRIBER_TYPE)
    return manager_class(settings)


