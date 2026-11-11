"""
test_settings.py

Creates isolated temporary settings for use in tests.
"""

from urllib.parse import urljoin
import tempfile
import os


class TestSettings:
    @staticmethod
    def generate():
        """
        Creates test settings with isolated temporary folders.
        """

        class _Settings:
            settings_name = "testing_settings"
            host = "localhost"
            port = 8000

            DownloaderHost = "localhost"
            ConverterHost = "localhost"
            TranscriberHost = "localhost"

            DownloaderPort = 8001
            ConverterPort = 8002
            TranscriberPort = 8003

            DownloaderURL = "/download"
            ConverterURL = "/convert"
            TranscriberURL = "/transcribe"

            STORAGE_TYPE = "local"
            TOOLS_FOLDER = "tools"

            mongo_url = mongo_url = "mongodb://admin:test_password@localhost:27017/?authSource=admin"
            db_name = "test_gateway_db"
            collection_name = "test_jobs"
            MAX_UPLOAD_MB = 100

            DOWNLOADER_OUTPUT_DIR = tempfile.mkdtemp()
            CONVERTER_OUTPUT_DIR = tempfile.mkdtemp()
            TRANSCRIBER_OUTPUT_DIR = tempfile.mkdtemp()
            UPLOADED_FILES_DIR = tempfile.mkdtemp()
            TEST_FOLDER = os.path.join(
                                        os.path.dirname(os.path.abspath(__file__)),
                                        "files"
                                    )

            UploadedFilesDir = UPLOADED_FILES_DIR

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

        return _Settings()