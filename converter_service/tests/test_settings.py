"""
test_settings.py

Creates isolated temporary settings for use in tests.
"""


import tempfile
import os

class TestSettings:
    @staticmethod
    def generate():   # to create unique temporary folders for each test to ensure isolation.
        class _Settings:
            TEMP_DIR_OUTPUT = tempfile.mkdtemp()
            TOOLS_FOLDER = tempfile.mkdtemp()
            STORAGE_TYPE = "local"
            DEBUG_PROGRESS = "False"
            DOCS_DIR = os.path.abspath("docs")
            TEST_FOLDER = "tests/files"
        return _Settings()
