"""
utils.py

Helper functions for integration tests: API calls, dummy file preparation,
test case loading, and common assertions.
"""

from app.models.micro_schemas import DownloaderResponseData, ConverterResponseData, TranscriberResponseData
import tests.shared_helpers.testing_constants as tc

def create_microservices_mocks(mock_pipeline_clients,
                               converter_side_effect = None,
                               downloader_side_effect = None,
                               downloader_file_path = None,
                               transcriber_file_path = None):
    
    MockDownloader, MockConverter, MockTranscriber = mock_pipeline_clients
    if downloader_file_path is None:
        downloader_file_path=tc.TEST_VIDEO_PATH
    MockDownloader.return_value.download.return_value = DownloaderResponseData(file_path=downloader_file_path,
                                                                                    file_name = tc.TEST_FILE_NAME,
                                                                                    file_extension=tc.TEST_VIDEO_EXTENSION)
    if downloader_side_effect is not None:
        MockDownloader.return_value.download.side_effect = downloader_side_effect

    MockConverter.return_value.convert.return_value = ConverterResponseData(file_path=tc.TEST_AUDIO_PATH,
                                                                                file_name = tc.TEST_FILE_NAME,
                                                                                file_extension=tc.TEST_AUDIO_EXTENSION)
    if converter_side_effect is not None:
        MockConverter.return_value.convert.side_effect = converter_side_effect

    if transcriber_file_path is None:
        transcriber_file_path = tc.TEST_TRANSCRIBE_PATH

    MockTranscriber.return_value.transcribe.return_value = TranscriberResponseData(file_path=transcriber_file_path)


