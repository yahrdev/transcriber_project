"""
test_job_pipeline.py

Unit tests for JobPipeline from job_pipeline.py.

start_* methods run in the gateway: they create the job and enqueue a Celery task.
run_*   methods run in the Celery worker: they do the actual processing.

Celery and Redis are not used in these tests: .delay() is patched.
"""

import os
import unittest
import uuid
from io import BytesIO
from unittest.mock import patch, Mock

import requests

from app.services.job_pipeline import JobPipeline
from app.exceptions.exceptions import AppError
from app.models.api_schemas import SourceData, PostResponseData, ResponseDataModel
from app.models.micro_schemas import DownloaderResponseData, ConverterResponseData, TranscriberResponseData
from app.models.job_schemas import JobStatus
from tests.testing_settings import TestSettings
import tests.shared_helpers.testing_constants as tc


UPLOAD_DELAY = "app.tasks.transcribe_upload_job.delay"
REFERENCE_DELAY = "app.tasks.transcribe_reference_job.delay"


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

        self.job_id = str(uuid.uuid4())
        self.test_file_path_video = tc.TEST_VIDEO_PATH
        self.test_file_name = tc.TEST_FILE_NAME
        self.test_file_extension_video = tc.TEST_VIDEO_EXTENSION
        self.test_file_path_audio = tc.TEST_AUDIO_PATH
        self.test_file_extension_audio = tc.TEST_AUDIO_EXTENSION
        self.test_file_path_transcibe = tc.TEST_TRANSCRIBE_PATH

        self.test_file = Mock()
        self.test_file.filename = tc.TEST_VIDEO_FILE
        self.test_file.file = BytesIO(b"fake video content")
        self.test_file.size = 100  # bytes; must be a real number for the size check

        self.testing_data = SourceData(client_id="test_id",
                                       source_type="path",
                                       source=self.test_file_path_video,
                                       language="en")

    # ---------- helpers ----------

    def mock_services(self, download_side_effect=None, converter_side_effect=None):
        """Sets return values (or errors) for downloader, converter and transcriber mocks."""
        self.jp.downloader.download.return_value = DownloaderResponseData(
            file_path=self.test_file_path_video,
            file_name=self.test_file_name,
            file_extension=self.test_file_extension_video)
        self.jp.downloader.download.side_effect = download_side_effect

        self.jp.converter.convert.return_value = ConverterResponseData(
            file_path=self.test_file_path_audio,
            file_name=self.test_file_name,
            file_extension=self.test_file_extension_audio)
        self.jp.converter.convert.side_effect = converter_side_effect

        self.jp.transcriber.transcribe.return_value = TranscriberResponseData(
            file_path=self.test_file_path_transcibe)

    def assert_queued(self, result):
        """start_* must return job_id immediately, without a result."""
        self.assertIsInstance(result, PostResponseData)
        self.assertIsNone(result.data)

    def assert_completed(self, result):
        """run_* must return the path to the transcription."""
        self.assertIsInstance(result, PostResponseData)
        self.assertIsInstance(result.data, ResponseDataModel)
        self.assertEqual(result.data.result_url, self.test_file_path_transcibe)

    def assert_first_status_processing(self):
        """The worker must mark the job as processing before doing anything else."""
        first_call = self.jp.js.update_document.call_args_list[0]
        self.assertEqual(first_call.kwargs["job_status"], JobStatus.processing)

    def assert_failed(self, expected_code):
        """The last status update must be 'failed' with the expected error code."""
        last_call = self.jp.js.update_document.call_args_list[-1]
        self.assertEqual(last_call.kwargs["job_status"], JobStatus.failed)
        self.assertEqual(last_call.kwargs["error"].code, expected_code)

    # ---------- start_upload (gateway) ----------

    def test_start_upload(self):
        self.jp.file_manager.create_tmp_file_path.return_value = (self.test_file_path_video,
                                                                  self.test_file_name)
        with (
            patch("app.services.job_pipeline.validate_language", return_value="en"),
            patch("app.services.job_pipeline.validate_media_mime"),
            patch("app.services.job_pipeline.validate_media_file"),
            patch("app.services.job_pipeline.extract_extension",
                  return_value=self.test_file_extension_video),
            patch(UPLOAD_DELAY) as mock_delay,
        ):
            result = self.jp.start_upload(client_id=self.testing_data.client_id,
                                          language="en",
                                          file=self.test_file)

        self.assert_queued(result)
        self.jp.js.create_document.assert_called_once()
        mock_delay.assert_called_once_with(job_id=str(result.job_id),
                                           language="en",
                                           tmp_path=self.test_file_path_video,
                                           file_name=self.test_file_name,
                                           file_extension=self.test_file_extension_video)

    def test_start_upload_file_too_big(self):
        self.test_file.size = self.settings.MAX_UPLOAD_MB * 1024 * 1024 + 1

        with (
            patch("app.services.job_pipeline.validate_language", return_value="en"),
            patch(UPLOAD_DELAY) as mock_delay,
        ):
            with self.assertRaises(AppError) as ctx:
                self.jp.start_upload(client_id=self.testing_data.client_id,
                                     language="en",
                                     file=self.test_file)

        self.assertEqual(ctx.exception.code, "BIG_FILE")
        self.assert_failed("BIG_FILE")
        mock_delay.assert_not_called()

    # ---------- start_reference (gateway) ----------

    def test_start_reference(self):
        with (
            patch("app.services.job_pipeline.validate_language", return_value="en"),
            patch(REFERENCE_DELAY) as mock_delay,
        ):
            result = self.jp.start_reference(self.testing_data)

        self.assert_queued(result)
        self.jp.downloader.download.assert_not_called()  # downloading happens in the worker now
        mock_delay.assert_called_once_with(job_id=str(result.job_id),
                                           source_type="path",
                                           source=self.test_file_path_video,
                                           language="en")

    def test_start_reference_db_error(self):
        self.jp.js.create_document.side_effect = Exception("Mongo is down")

        with (
            patch("app.services.job_pipeline.validate_language", return_value="en"),
            patch(REFERENCE_DELAY) as mock_delay,
        ):
            with self.assertRaises(AppError) as ctx:
                self.jp.start_reference(self.testing_data)

        self.assertEqual(ctx.exception.code, "CAN_NOT_CREATE_DOCUMENT")
        mock_delay.assert_not_called()

    # ---------- run_reference (worker) ----------

    def test_run_reference(self):
        self.mock_services()

        with patch("app.services.job_pipeline.validate_media_file"):
            result = self.jp.run_reference(job_id=self.job_id,
                                           source_type="path",
                                           source=self.test_file_path_video,
                                           language="en")

        self.assert_completed(result)
        self.assert_first_status_processing()
        self.jp.file_manager.clear_temp_folders.assert_called_once_with(self.test_file_name)

    def test_run_reference_download_error(self):
        self.mock_services(download_side_effect=requests.exceptions.ConnectionError())

        with patch("app.services.job_pipeline.validate_media_file"):
            with self.assertRaises(requests.exceptions.ConnectionError):
                self.jp.run_reference(job_id=self.job_id,
                                      source_type="path",
                                      source=self.test_file_path_video,
                                      language="en")

        self.assert_failed("ConnectionError")
        self.jp.converter.convert.assert_not_called()
        self.jp.file_manager.clear_temp_folders.assert_not_called()  # nothing was downloaded

    # ---------- run_upload (worker) ----------

    def test_run_upload(self):
        self.mock_services()

        result = self.jp.run_upload(job_id=self.job_id,
                                    language="en",
                                    tmp_path=self.test_file_path_video,
                                    file_name=self.test_file_name,
                                    file_extension=self.test_file_extension_video)

        self.assert_completed(result)
        self.assert_first_status_processing()
        self.jp.converter.convert.assert_called_once_with(file_path=self.test_file_path_video,
                                                          target_filename=self.test_file_name,
                                                          source_extension=self.test_file_extension_video,
                                                          target_extension="wav")
        self.jp.file_manager.clear_temp_folders.assert_called_once_with(self.test_file_name)

    def test_run_upload_converter_error(self):
        self.mock_services(converter_side_effect=requests.exceptions.ConnectionError())

        with self.assertRaises(requests.exceptions.ConnectionError):
            self.jp.run_upload(job_id=self.job_id,
                               language="en",
                               tmp_path=self.test_file_path_video,
                               file_name=self.test_file_name,
                               file_extension=self.test_file_extension_video)

        self.assert_failed("ConnectionError")
        self.jp.transcriber.transcribe.assert_not_called()
        self.jp.file_manager.clear_temp_folders.assert_called_once_with(self.test_file_name)  # cleanup even on error


# python -m unittest discover -s tests/unit -p "test_job_pipeline.py" -v
# python -m unittest tests.unit.test_job_pipeline.TestJobPipeline.test_start_upload -v