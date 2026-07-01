"""
test_file_manager.py

Unit tests for LocalStorageFileManager from file_manager.py.
"""

from app.core.file_manager import LocalStorageFileManager
import unittest
from tests.test_settings import TestSettings
import os
import shutil

class TestLocalStorageFileManager(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.fm = LocalStorageFileManager(self.settings)

    def tearDown(self):
        shutil.rmtree(self.settings.TEMP_DIR_OUTPUT)

    def test_get_tmp_dir(self):
        """"
        Happy path: get_tmp_dir returns correct directory
        """
        returndir = self.fm.get_tmp_dir()
        self.assertEqual(returndir, self.settings.TEMP_DIR_OUTPUT)


    def test_create_tmp_file_path(self):
        """
        Creates tmp file with specified filename
        """

        ext = "wav"
        filename = "test"
        returndir, filename = self.fm.create_tmp_file_path(ext, filename)
        self.assertEqual(returndir, os.path.join(self.settings.TEMP_DIR_OUTPUT, f"{filename}.{ext}"))


    def test_filename_create_tmp_file_path(self):
        """
        Creates tmp file with auto-generated filename
        """

        ext = "wav"
        returndir, filename = self.fm.create_tmp_file_path(ext)
        self.assertTrue(filename)
        self.assertTrue(returndir.startswith(self.settings.TEMP_DIR_OUTPUT))





#python -m unittest discover -s tests -p "*.py" -v
#python -W ignore::ResourceWarning -m unittest discover -s tests/unit -p "test_file_manager.py" -v
