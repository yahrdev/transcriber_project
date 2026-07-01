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
            TEST_FOLDER = "tests/files"
            PORT: int = 8001
        return _Settings()
    



