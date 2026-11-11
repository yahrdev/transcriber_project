"""
config.py

This module reads and provides application configuration settings.
"""
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from urllib.parse import urljoin


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# def abs_path(value: str) -> str:
#     return value if os.path.isabs(value) else os.path.join(BASE_DIR, value)

class Settings(BaseSettings):
    settings_name: str = "prod_settings"
    MAX_UPLOAD_MB: int = 100
    DownloaderURL: str
    ConverterURL: str
    TranscriberURL: str
    host: str
    port: int
    DownloaderPort: int
    ConverterPort: int
    TranscriberPort: int
    DownloaderHost: str
    ConverterHost: str
    TranscriberHost: str
    UploadedFilesDir: str
    STORAGE_TYPE: str = "local"   # Directory where files are currently saved
    TOOLS_FOLDER: str  # The folder for saving executables like ffmpeg for converting
    mongo_url: str
    db_name: str
    collection_name: str
    DOWNLOADER_OUTPUT_DIR: str
    CONVERTER_OUTPUT_DIR: str
    TRANSCRIBER_OUTPUT_DIR: str
    UPLOADED_FILES_DIR: str
    REDIS_URL: str
    

    model_config = ConfigDict(env_file = ".env")

    @property
    def http_base(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def downloader_url(self) -> str:
        base = f"http://{self.DownloaderHost}:{self.DownloaderPort}"
        return urljoin(base, self.DownloaderURL)
    
    @property
    def converter_url(self) -> str:
        base = f"http://{self.ConverterHost}:{self.ConverterPort}"
        return urljoin(base, self.ConverterURL)
    
    @property
    def transcriber_url(self) -> str:
        base = f"http://{self.TranscriberHost}:{self.TranscriberPort}"
        return urljoin(base, self.TranscriberURL)

settings = Settings()