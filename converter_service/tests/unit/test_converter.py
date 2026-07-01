"""
test_converter.py

Unit tests for Converter subclasses from converter.py.
"""

import unittest
from app.core.converter import ConvertVideoAudio
from app.core.file_manager import LocalStorageFileManager
from tests.test_settings import TestSettings
import shutil
import os
from app.exceptions.exceptions import AppError
import tests.shared_helpers.dummy_generators as dg

class TestConvertVideoAudio(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.fm = LocalStorageFileManager(self.settings)
        self.converter = ConvertVideoAudio(self.settings, self.fm)


    def tearDown(self):
        shutil.rmtree(self.settings.TEMP_DIR_OUTPUT)


    def test_convert(self):
        """"
        Happy path: successful conversion
        """

        video_path = os.path.join(self.settings.TEST_FOLDER, "test.mp4")
        dg.create_dummy_video(video_path)
        output_data = self.converter.convert(input_path=video_path, 
                                             extension_from="mp4", 
                                             file_name="test", 
                                             extension_to="wav")
        self.assertTrue(output_data.file_path.endswith(".wav"))
        self.assertEqual(output_data.file_extension, "wav")
        self.assertEqual(output_data.file_name, "test")



    def test_wrong_extension_convert(self):
        """
        Unhappy path: extension mismatch
        """

        file_path = os.path.join(self.settings.TEST_FOLDER, "test_text.txt")
        with open(file_path, "w") as f:
            f.write("Some test content")  
        with self.assertRaises(AppError) as context:
            output_data = self.converter.convert(input_path=file_path, 
                                                 extension_to="mp4", 
                                                 file_name="test_text", 
                                                 extension_from="wav")
        self.assertEqual(context.exception.code, "EXTENSION_MISMATCH")


    def test_not_media_convert(self):
        """
        Unhappy path: file is not a valid media file
        """

        file_path = os.path.join(self.settings.TEST_FOLDER, "test_video.mp4")
        with open(file_path, "w") as f:
            f.write("Some test content")
        with self.assertRaises(AppError) as context:
            output_data = self.converter.convert(input_path=file_path, 
                                                 extension_to="mp3", 
                                                 file_name="test_video", 
                                                 extension_from="mp4")
        self.assertEqual(context.exception.code, "FILE_WRONG_TYPE")

#python -W ignore::ResourceWarning -m unittest discover -s tests/unit -p "test_converter.py" -v