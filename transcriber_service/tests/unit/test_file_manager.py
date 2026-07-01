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
        os.makedirs(self.settings.CHUNKS, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.settings.TEMP_DIR_OUTPUT):
            shutil.rmtree(self.settings.TEMP_DIR_OUTPUT)
        if os.path.exists(self.settings.CHUNKS):
            shutil.rmtree(self.settings.CHUNKS)

    def test_get_tmp_dir(self):
        """"
        Should successfully return correct directory
        """
        returndir = self.fm.get_tmp_dir()
        self.assertEqual(os.path.normpath(returndir), os.path.normpath(self.settings.TEMP_DIR_OUTPUT))



    def test_create_tmp_file_path(self):
        """
        Creates tmp file with specified filename
        """

        ext = "txt"
        testfilename = "testfile"
        subfolder = f"{uuid.uuid4()}"
        dir_to_check = os.path.join(self.settings.CHUNKS, subfolder)
        returned_path, filename = self.fm.create_tmp_file_path(extension=ext, filename=testfilename, type='chunk', subfolder=subfolder)
        returned_path = os.path.abspath(returned_path)
        dir_to_check = os.path.abspath(dir_to_check)
        self.assertEqual(
            os.path.commonpath([returned_path, dir_to_check]),
            os.path.normpath(dir_to_check)
        )  #find the same part in both paths
        self.assertTrue(returned_path.endswith(f"{testfilename}.{ext}"))


    def test_filename_create_tmp_file_path(self):
        """
        Creates tmp file with auto-generated filename
        """

        ext = "wav"
        returned_path, filename = self.fm.create_tmp_file_path(ext)
        self.assertTrue(filename)
        returned_path = os.path.normpath(returned_path)
        self.assertTrue(returned_path.startswith(os.path.normpath(self.settings.TEMP_DIR_OUTPUT)))
        self.assertTrue(returned_path.endswith(f"{filename}.{ext}"))



    
    def test_save_to_tmp(self):
        """
        Saves text to tmp folder
        """

        testfilename = "testfile.txt"
        subfolder = f"{uuid.uuid4()}"
        returned_path, filename = self.fm.create_tmp_file_path(extension='txt', filename=testfilename, type='chunk', subfolder=subfolder)
        self.fm.save_to_tmp(returned_path, source="Some test content")
        with open(returned_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "Some test content")

    def test_save_to_tmp_invalid_source(self):
        """
        Raises AppError for invalid source type
        """

        testfilename = "testfile.txt"
        subfolder = f"{uuid.uuid4()}"
        returned_path, filename = self.fm.create_tmp_file_path(extension='txt', filename=testfilename, type='chunk', subfolder=subfolder)
        testingset = set()
        with self.assertRaises(AppError) as context:
            self.fm.save_to_tmp(returned_path, source=testingset)
        self.assertEqual(context.exception.code, "SOURCE_IS_EMPTY_OR_INVALID")


    def test_save_to_tmp_list(self):
        """
        Saves text to tmp folder
        """

        testfilename = "testfile.txt"
        subfolder = f"{uuid.uuid4()}"
        returned_path, filename = self.fm.create_tmp_file_path(extension='txt', filename=testfilename, type='chunk', subfolder=subfolder)
        testinglist = ['test1', 'test2']
        self.fm.save_to_tmp(returned_path, source=testinglist)
        with open(returned_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "\n".join(testinglist))


#python -m unittest discover -s tests -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "test_file_manager.py" -v
