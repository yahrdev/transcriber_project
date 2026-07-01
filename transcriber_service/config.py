"""
config.py

This module reads and provides application configuration settings.
"""
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def abs_path(value: str) -> str:
    return value if os.path.isabs(value) else os.path.join(BASE_DIR, value)

class Settings(BaseSettings):
    TEMP_DIR_OUTPUT: str = abs_path(os.getenv("TEMP_DIR_OUTPUT", "tmp/transcriber_output"))  # Temporary folder to store the file after transcribing
    STORAGE_TYPE: str = "local"   # Directory where files are currently saved
    DEBUG_PROGRESS: str = "false"  # Flag to enable or disable debug progress output
    TRANSCRIBER_TYPE: str = "api"
    CHUNKS: str = abs_path(os.getenv("CHUNKS", "chunks"))
    OPEN_AI_KEY: str = ""
    PORT: int = 8003

    model_config = ConfigDict(env_file = ".env")

settings = Settings()