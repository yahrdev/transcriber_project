"""
config.py

The module for reading configurations
"""
import os
from dotenv import load_dotenv

from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def abs_path(value: str) -> str:
    return value if os.path.isabs(value) else os.path.join(BASE_DIR, value)

class Settings(BaseSettings):
    DEBUG_PROGRESS: bool = False
    PORT: int
    HOST: str
    BACKEND_PORT:str




    @property
    def http_base(self) -> str:
        return f"http://{self.HOST}:{self.BACKEND_PORT}"

    

settings = Settings()