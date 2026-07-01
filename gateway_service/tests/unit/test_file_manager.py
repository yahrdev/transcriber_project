"""
test_file_manager.py

Unit tests for LocalStorageFileManager from file_manager.py.
"""

from app.services.file_manager import LocalStorageFileManager
import unittest
from tests.testing_settings import TestSettings
import os
import shutil
from app.exceptions.exceptions import AppError
import tests.shared_helpers.testing_constants as tc

class TestLocalStorageFileManager(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.fm = LocalStorageFileManager(self.settings)
        self.test_txt_filepath = os.path.join(self.settings.TEST_FOLDER, tc.TEST_TXT_FILE)

    def tearDown(self):
        if os.path.exists(self.settings.UploadedFilesDir):
            shutil.rmtree(self.settings.UploadedFilesDir)

        

    def read_testing_file(self, source_path, mode = "r"):
        with open(source_path, mode) as f:
            return f.read()



    def test_get_tmp_dir(self):
        """"
        Should successfully return correct directory
        """
        returndir = self.fm.get_tmp_dir()
        self.assertEqual(os.path.normpath(returndir), os.path.normpath(self.settings.UploadedFilesDir))



    def test_create_tmp_file_path(self):
        """
        Creates tmp file with specified file_name
        """

        ext = tc.TEST_TXT_FILE_EXT
        testfilename = tc.TEST_TXT_FILE_NAME
        returndir, file_name = self.fm.create_tmp_file_path(file_extension = ext, file_name=testfilename)
        self.assertEqual(
            os.path.commonpath([returndir, self.settings.UploadedFilesDir]),
            os.path.normpath(self.settings.UploadedFilesDir)
        )


    def test_filename_create_tmp_file_path(self):
        """
        Creates tmp file with auto-generated filename
        """

        ext = "wav"
        returned_path, filename = self.fm.create_tmp_file_path(file_extension=ext)
        self.assertTrue(filename)
        returned_path = os.path.normpath(returned_path)
        self.assertTrue(returned_path.startswith(os.path.normpath(self.settings.UploadedFilesDir)))
        self.assertTrue(returned_path.endswith(f"{filename}.{ext}"))



    
    def test_save_to_tmp(self):
        """
        Saves text to tmp folder
        """

        testfilename = tc.TEST_TXT_FILE
        returned_path, filename = self.fm.create_tmp_file_path(file_extension='txt', file_name=testfilename)
        source = self.read_testing_file(self.test_txt_filepath, mode="rb")
        self.fm.save_to_tmp(returned_path, source=source)
        content = self.read_testing_file(returned_path)
        expected = self.read_testing_file(self.test_txt_filepath)
        self.assertEqual(content, expected)


    def test_save_to_tmp_invalid_source(self):
        """
        Raises AppError for invalid source type
        """

        testfilename = tc.TEST_TXT_FILE
        returned_path, filename = self.fm.create_tmp_file_path(file_extension=tc.TEST_TXT_FILE_EXT, file_name=testfilename)
        testingset = set()
        with self.assertRaises(AppError) as context:
            self.fm.save_to_tmp(returned_path, source=testingset)
        self.assertEqual(context.exception.code, "SOURCE_IS_EMPTY_OR_INVALID")



    


#python -m unittest discover -s tests -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "test_file_manager.py" -v
