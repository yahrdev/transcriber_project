"""
test_downloader.py

Unit tests for Downloader subclasses from extractor.py.
"""

import unittest
from app.core.extractor import FileExtractorURL, FileExtractorPath
from app.core.file_manager import LocalStorageFileManager
from tests.test_settings import TestSettings
import shutil
import os
from app.exceptions.exceptions import AppError
import tests.shared_helpers.models as m
from typing import Optional
from unittest.mock import patch

class TestFileExtractorURL(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.fm = LocalStorageFileManager(self.settings)
        self.extractor = FileExtractorURL(self.settings, self.fm)
        self.authinfo = m.AuthNone(method="none")


    def tearDown(self):
        if os.path.exists(self.settings.TEMP_DIR_OUTPUT):
            shutil.rmtree(self.settings.TEMP_DIR_OUTPUT)


    def test_extractor(self):
        """"
        Should successfully extract file from valid URL
        """
        
        source = 'https://filesamples.com/samples/video/mp4/sample_640x360.mp4'
        response: Optional[m.ResponseData] = None
        with patch("app.core.extractor.get_request_content", return_value=b"fake-mp4-bytes"):
            response = self.extractor.extract(auth=self.authinfo, source=source)
        if response:
            self.assertTrue(os.path.exists(response.file_path))
            self.assertTrue(response.file_path.endswith(".mp4"))
        else:
            self.fail("Response is empty — the file was not extracted.")

        
    def test_unreachable_url_file(self):
        """
        Should return error unreachable input file url
        """

        source = 'https://filesamples.com/samples/video/mp4/sampl0.mp4'
        with patch("app.core.extractor.get_request_content", side_effect=AppError("URL_UNREACHABLE", url=source)):
            with self.assertRaises(AppError) as context:
                self.extractor.extract(auth=self.authinfo, source=source)
        self.assertEqual(context.exception.code, "URL_UNREACHABLE")



    def test_wrong_extension(self):
        """
        Should return error about invalid file path
        """

        source = 'https://filesamples.com/samples/video/mp4/sample_640x360'
        
        with patch("app.core.extractor.get_request_content", return_value=b"fake-mp4-bytes"):
            with self.assertRaises(AppError) as context:
                self.extractor.extract(auth=self.authinfo, source=source)
        self.assertEqual(context.exception.code, "INVALID_FILE_PATH")




class TestFileExtractorPath(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.fm = LocalStorageFileManager(self.settings)
        self.extractor = FileExtractorPath(self.settings, self.fm)
        os.makedirs(self.settings.TEST_FOLDER, exist_ok=True)
        self.authinfo = m.AuthNone(method="none")
        


    def tearDown(self):
        shutil.rmtree(self.settings.TEMP_DIR_OUTPUT)
        shutil.rmtree(self.settings.TEST_FOLDER)


    def test_extractor(self):
        """
        Should successfully extract file from valid path
        """
        
        response: Optional[m.ResponseData] = None
        testfilename = "testfile.txt"
        testfilepath = os.path.join(self.settings.TEST_FOLDER, testfilename)
        with open(testfilepath, "w") as f:
            f.write("Some test content")
        response = self.extractor.extract(auth=self.authinfo, source=testfilepath)
        if response:
            self.assertTrue(os.path.exists(response.file_path))
            self.assertTrue(response.file_path.endswith(".txt"))
        else:
            self.fail("Response is empty — the file was not extracted.")

        


    def test_not_found_file(self):
        """
        Should return error file not found
        """

        testfilename = "testfile.txt"
        testfilepath = os.path.join(self.settings.TEST_FOLDER, testfilename)
        with self.assertRaises(AppError) as context:
            self.extractor.extract(auth=self.authinfo, source=testfilepath)
        self.assertEqual(context.exception.code, "FILE_NOT_FOUND_PATH")



    def test_wrong_extension(self):
        """
        Should return error invalid file path
        """

        testfilename = "testfile.xyz"
        testfilepath = os.path.join(self.settings.TEST_FOLDER, testfilename)
        with self.assertRaises(AppError) as context:
            self.extractor.extract(auth=self.authinfo, source=testfilepath)
        self.assertEqual(context.exception.code, "UNSUPPORTED_EXTENSION")

#python -m unittest discover -s tests/unit -p "test_downloader.py" -v