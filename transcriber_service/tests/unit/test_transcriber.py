"""
test_transcriber.py

Unit tests for transcriber subclasses from transcriber.py.
"""

import unittest
from app.core.transcriber import MockTranscribeByAPI
from app.core.file_manager import LocalStorageFileManager
from tests.test_settings import TestSettings
import shutil
import os
from app.exceptions.exceptions import AppError
import tests.shared_helpers.models as m
from typing import Optional
from pydub import AudioSegment

class TestTranscriber(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.fm = LocalStorageFileManager(self.settings)
        self.transcriber = MockTranscribeByAPI(self.settings, self.fm)
        os.makedirs(self.settings.CHUNKS, exist_ok=True)
        audio = AudioSegment.silent(duration=1000) 
        self.testfilepath = os.path.join(self.settings.TEST_FOLDER, 'testaudio.mp3')
        audio.export(self.testfilepath, format="mp3")


    def tearDown(self):
        if os.path.exists(self.settings.TEMP_DIR_OUTPUT):
            shutil.rmtree(self.settings.TEMP_DIR_OUTPUT)
        if os.path.exists(self.settings.CHUNKS):
            shutil.rmtree(self.settings.CHUNKS)


    def test_transcriber_success_empty_params(self):
        """"
        Should successfully transcribe file
        """
        
        response: Optional[m.ResponseData] = None
        response = self.transcriber.transcribe(audio_file_path=self.testfilepath, 
                                               audio_file_name='Transcribed', 
                                               target_extension='', 
                                               language='')
        self.assertTrue(os.path.exists(response.file_path))
        self.assertTrue(response.file_path.endswith(".txt"))
        with open(response.file_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Mock Transcribation text", content)




    def test_transcriber_success_filled_params(self):
        """"
        Should successfully transcribe file
        """
        
        response = self.transcriber.transcribe(audio_file_path=self.testfilepath, 
                                               audio_file_name='Transcribed', 
                                               target_extension='pdf', 
                                               language='ua')
        self.assertTrue(os.path.exists(response.file_path))
        self.assertTrue(response.file_path.endswith(".pdf"))
        with open(response.file_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Mock Transcribation text", content)


    def test_not_found_file(self):
        """
        Should return error file not found
        """

        source = os.path.join(self.settings.TEST_FOLDER, 'testaudio_fake.mp3')
        with self.assertRaises(AppError) as context:
            self.transcriber.transcribe(audio_file_path=source, 
                                        audio_file_name='Transcribed', 
                                        target_extension='pdf', 
                                        language='ua')
        self.assertEqual(context.exception.code, "FILE_NOT_FOUND_PATH")



    def test_wrong_extension(self):
        """
        Should return error about invalid file extension
        """

        testfilepath_wrong_ext = os.path.join(self.settings.TEST_FOLDER, "testfile.txt")
        with open(testfilepath_wrong_ext, "w") as f:
            f.write("Some test content")
        with self.assertRaises(AppError) as context:
            self.transcriber.transcribe(audio_file_path=testfilepath_wrong_ext, 
                                        audio_file_name='Transcribed', 
                                        target_extension='', 
                                        language='')
        self.assertEqual(context.exception.code, "UNSUPPORTED_EXTENSION")


    





#python -W ignore::ResourceWarning -m unittest discover -s tests/unit -p "test_transcriber.py" -v