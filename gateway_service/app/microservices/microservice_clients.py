"""
Provides typed clients for downloader, converter, and transcriber services.
"""

import requests
import app.models.micro_schemas as s
from app.exceptions.exceptions import MicroserviceError
from typing import Optional
from app.microservices.connections import create_and_post


class DownloaderClient:
    def __init__(self, settings, file_manager=None):
        self.file_manager = file_manager 
        #or get_file_manager(settings)
        self._settings = settings

    def download(self, source_type:str, source: str) -> s.DownloaderResponseData:
        data = s.DownloaderSourceData(source_type=source_type, 
                                      source=source, 
                                      auth=s.AuthNone(method="none"))
        return create_and_post(request_model= data, 
                                response_model=s.DownloaderResponseData,
                               url = self._settings.downloader_url, 
                               service_name="downloader_service")


class ConverterClient:

    def __init__(self, settings, file_manager=None):
        self.file_manager = file_manager 
        #or get_file_manager(settings)
        self._settings = settings

    def convert(self, file_path: str, target_filename :str,  target_extension: str, source_extension: str = None):
        data = s.ConverterSourceData(file_path = file_path,
                                    target_filename = target_filename,
                                    source_extension = source_extension,
                                    target_extension = target_extension)
        return create_and_post(request_model = data, 
                               response_model=s.ConverterResponseData,
                                url = self._settings.converter_url, 
                                service_name="converter_service")


class TranscriberClient:

    def __init__(self, settings, file_manager=None):
        self.file_manager = file_manager 
        #or get_file_manager(settings)
        self._settings = settings

    def transcribe(self, file_path:str, file_name: str,target_extension: str,language: str):
        data = s.TranscriberSourceData(file_path = file_path,
                                        file_name = file_name,
                                        target_extension = target_extension,
                                        language = language)
        return create_and_post(request_model = data,
                               response_model= s.TranscriberResponseData, 
                                url = self._settings.transcriber_url, 
                                service_name="transcriber_service")
        