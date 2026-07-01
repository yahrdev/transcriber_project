"""
test_settings.py

Creates isolated temporary settings for use in tests.
"""


import tempfile

class TestSettings:
    @staticmethod
    def generate():   # to create unique temporary folders for each test to ensure isolation.
        class _Settings:
            TEMP_DIR_OUTPUT: str = tempfile.mkdtemp()  # Temporary folder to store the file after downloading
            STORAGE_TYPE: str = "local"   # Directory where files are currently saved
            DEBUG_PROGRESS: str = "false"  
            TRANSCRIBER_TYPE: str = "test_api"
            CHUNKS: str = "tests/files/chunks"
            OPEN_AI_KEY: str = ""
            TEST_FOLDER = "tests/files"
            PORT: int = 8003
        return _Settings()
    



