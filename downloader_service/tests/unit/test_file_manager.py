"""
test_file_manager.py

Unit tests for LocalStorageFileManager from file_manager.py.
"""

from app.core.file_manager import LocalStorageFileManager
import unittest
from tests.test_settings import TestSettings
import os
import shutil
import uuid
from app.exceptions.exceptions import AppError

class TestLocalStorageFileManager(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.fm = LocalStorageFileManager(self.settings)
        os.makedirs(self.settings.TEST_FOLDER, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.settings.TEMP_DIR_OUTPUT):
            shutil.rmtree(self.settings.TEMP_DIR_OUTPUT)
        if os.path.exists(self.settings.TEST_FOLDER):
            shutil.rmtree(self.settings.TEST_FOLDER)

    def test_get_tmp_dir(self):
        """"
        Should successfully return correct directory
        """
        returndir = self.fm.get_tmp_dir()
        self.assertEqual(os.path.normpath(returndir), os.path.normpath(self.settings.TEMP_DIR_OUTPUT))



    def test_create_tmp_file_path(self):
        """
        Creates tmp file with specified file_name
        """

        ext = "txt"
        testfilename = "testfile"
        returndir, file_name = self.fm.create_tmp_file_path(ext, testfilename)
        self.assertEqual(
            os.path.commonpath([returndir, self.settings.TEMP_DIR_OUTPUT]),
            os.path.normpath(self.settings.TEMP_DIR_OUTPUT)
        )

    def test_filename_create_tmp_file_path(self):
        """
        Creates tmp file with auto-generated file_name
        """

        ext = "wav"
        returndir, file_name = self.fm.create_tmp_file_path(ext)
        self.assertTrue(file_name)
        returndir = os.path.normpath(returndir)
        self.assertTrue(returndir.startswith(os.path.normpath(self.settings.TEMP_DIR_OUTPUT)))


    
    def test_save_to_tmp(self):
        """
        Saves file to tmp folder
        """

        testfilename = "testfile.txt"
        returned_path, file_name = self.fm.create_tmp_file_path(file_extension="txt", file_name=testfilename)
        testfilepath = os.path.join(self.settings.TEST_FOLDER, testfilename)
        with open(testfilepath, "w") as f:
            f.write("Some test content")
        self.fm.save_to_tmp(returned_path, testfilepath)
        with open(returned_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "Some test content")


    def test_save_to_tmp_invalid_source(self):
        """
        Raises AppError for invalid source type
        """

        testfilename = "testfile.txt"
        subfolder = f"{uuid.uuid4()}"
        returned_path, file_name = self.fm.create_tmp_file_path(file_extension='txt', file_name=testfilename)
        testingset = set()
        with self.assertRaises(AppError) as context:
            self.fm.save_to_tmp(returned_path, source=testingset)
        self.assertEqual(context.exception.code, "SOURCE_IS_EMPTY_OR_INVALID")




#python -m unittest discover -s tests -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "test_file_manager.py" -v
