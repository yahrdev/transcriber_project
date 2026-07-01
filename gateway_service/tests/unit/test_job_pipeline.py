"""
test_job_pipeline.py

Unit tests for JobPipeline from job_pipeline.py
"""

from app.services.job_pipeline import JobPipeline
import unittest
from tests.testing_settings import TestSettings
import os
from io import BytesIO
import requests
from unittest.mock import patch, Mock
from app.models.api_schemas import SourceData, PostResponseData, ResponseDataModel
from app.models.micro_schemas import DownloaderResponseData, ConverterResponseData, TranscriberResponseData
from app.models.job_schemas import JobStatus
import tests.shared_helpers.testing_constants as tc

class TestJobPipeline(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        with patch("app.services.job_pipeline.job_service.JobService"):
            self.jp = JobPipeline(self.settings)
        self.jp.downloader = Mock()
        self.jp.converter = Mock()
        self.jp.transcriber = Mock()
        self.jp.js = Mock()
        self.jp.file_manager = Mock()
        self.test_video_filepath = os.path.join(self.settings.TEST_FOLDER, tc.TEST_VIDEO_FILE)
        self.test_file_path_video= tc.TEST_VIDEO_PATH
        self.test_file_name = tc.TEST_FILE_NAME
        self.test_file_extension_video= tc.TEST_VIDEO_EXTENSION
        self.test_file_path_audio=tc.TEST_AUDIO_PATH
        self.test_file_extension_audio=tc.TEST_AUDIO_EXTENSION
        self.test_file_path_transcibe=tc.TEST_TRANSCRIBE_PATH
        self.test_file = Mock()
        self.test_file.filename = tc.TEST_VIDEO_FILE
        self.test_file.file = BytesIO(b"fake video content")
        self.testing_data = SourceData(client_id="test_id",
                          source_type="path",
                          source=self.test_file_path_video,
                          language="en")


    def tearDown(self):
        pass

    def create_mocks(self, mock_validate_language, 
                     mock_extract_extension = None, 
                     lang_return_value = None, 
                     ext_return_value = None,
                     create_file_return_value = None,
                     need_downloading = False,
                     download_side_effect = None,
                     converter_side_effect = None,
                     ):
        
        mock_validate_language.return_value = lang_return_value

        if mock_extract_extension is not None:
            mock_extract_extension.return_value = ext_return_value

        if create_file_return_value is not None:
            self.jp.file_manager.create_tmp_file_path.return_value = create_file_return_value

        if need_downloading:
            self.jp.downloader.download.return_value = DownloaderResponseData(file_path=self.test_file_path_video,
                                                                                    file_name = self.test_file_name,
                                                                                    file_extension=self.test_file_extension_video)
            if download_side_effect is not None:
                self.jp.downloader.download.side_effect = download_side_effect

        self.jp.converter.convert.return_value = ConverterResponseData(file_path=self.test_file_path_audio,
                                                                                file_name = self.test_file_name,
                                                                                file_extension=self.test_file_extension_audio)
        if converter_side_effect is not None:
            self.jp.converter.convert.side_effect = converter_side_effect

        self.jp.transcriber.transcribe.return_value = TranscriberResponseData(file_path=self.test_file_path_transcibe)



    def success_assert(self, result):
        self.assertIsInstance(result, PostResponseData)
        self.assertIsInstance(result.data, ResponseDataModel)
        response_data = result.data
        self.assertEqual(response_data.result_url, self.test_file_path_transcibe)
    
    def error_assert(self):
        last_call = self.jp.js.update_document.call_args_list[-1]
        kwargs = last_call.kwargs

        self.assertEqual(kwargs["job_status"], JobStatus.failed)
        self.assertEqual(kwargs["error"].code, "ConnectionError")


    def test_process_reference(self):
        
        with (
                patch("app.services.job_pipeline.validate_language") as mock_validate_language,
                patch("app.services.job_pipeline.validate_media_mime"),
                patch("app.services.job_pipeline.validate_media_file"),
            ):
            self.create_mocks(mock_validate_language,
                              lang_return_value=self.testing_data.language,
                              need_downloading=True)
            

            result = self.jp.process_reference(self.testing_data)

            self.success_assert(result=result)


    def test_process_reference_error(self):
        
        with (
                patch("app.services.job_pipeline.validate_language") as mock_validate_language,
                patch("app.services.job_pipeline.validate_media_mime"),
                patch("app.services.job_pipeline.validate_media_file"),
            ):
            self.create_mocks(mock_validate_language,
                              lang_return_value=self.testing_data.language,
                              need_downloading=True,
                              download_side_effect=requests.exceptions.ConnectionError())
            

            with self.assertRaises(requests.exceptions.ConnectionError):
                self.jp.process_reference(self.testing_data)

            self.error_assert()



    def test_process_upload(self):

        
        with (
                patch("app.services.job_pipeline.validate_language") as mock_validate_language,
                patch("app.services.job_pipeline.validate_media_mime"),
                patch("app.services.job_pipeline.validate_media_file"),
                patch("app.services.job_pipeline.extract_extension") as mock_extract_extension,
            ):
            self.create_mocks(mock_validate_language,
                              mock_extract_extension=mock_extract_extension,
                              lang_return_value=self.testing_data.language,
                              ext_return_value=self.test_file_extension_video,
                              create_file_return_value=(self.test_file_path_video, self.test_file_name)
                              )
            
            
            result = self.jp.process_upload(client_id = self.testing_data.client_id, 
                                            language = self.testing_data.language, 
                                            file = self.test_file)
            
            self.success_assert(result=result)



    def test_process_upload_error(self):

            
            with (
                    patch("app.services.job_pipeline.validate_language") as mock_validate_language,
                    patch("app.services.job_pipeline.validate_media_mime"),
                    patch("app.services.job_pipeline.validate_media_file"),
                    patch("app.services.job_pipeline.extract_extension") as mock_extract_extension,
                ):

                self.create_mocks(mock_validate_language,
                              mock_extract_extension=mock_extract_extension,
                              lang_return_value=self.testing_data.language,
                              ext_return_value=self.test_file_extension_video,
                              create_file_return_value=(self.test_file_path_video, self.test_file_name),
                              converter_side_effect=requests.exceptions.ConnectionError()
                              )

                with self.assertRaises(requests.exceptions.ConnectionError):
                    self.jp.process_upload(client_id = self.testing_data.client_id, 
                                            language = self.testing_data.language, 
                                            file = self.test_file)
                self.error_assert()


    


#python -m unittest discover -s tests/unit -p "test_job_pipeline.py" -v
#python -m unittest tests.unit.test_job_pipeline.TestJobPipeline.test_process_upload_error