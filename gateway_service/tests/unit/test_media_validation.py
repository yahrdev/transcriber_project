"""
test_media_validation.py

Unit tests for media_validation.py
"""

import unittest
from tests.testing_settings import TestSettings
import os
from app.exceptions.exceptions import AppError
from app.services.media_validation import validate_media_file, validate_media_mime, validate_language
from tests.unit.data import media_validation_test_cases as mv_cases
import tests.shared_helpers.testing_constants as tc

class TestMediaValidation(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.test_video_filepath = os.path.join(self.settings.TEST_FOLDER, tc.TEST_VIDEO_FILE)
        self.test_txt_filepath = os.path.join(self.settings.TEST_FOLDER, tc.TEST_TXT_FILE)
        self.test_corrupted_filepath = os.path.join(self.settings.TEST_FOLDER, tc.TEST_CORRUPTED_FILE)

    def tearDown(self):
        pass



    def test_validate_media_mime(self):
        cases = mv_cases.validate_media_mime_test_cases
        for case_name, case in cases.items():
            with self.subTest(case=case_name):
                if case["expected_error"]:
                    source_path = case["filepath"].format(filepath = self.test_txt_filepath)
                else:
                    source_path = case["filepath"].format(filepath = self.test_video_filepath)

                if case["source_type"] == "bytes":
                    with open(source_path, "rb") as f:
                        source = f.read()
                else:
                    source = source_path

                if case["expected_error"]:
                    with self.assertRaises(AppError) as context:
                        validate_media_mime(source)

                    self.assertEqual(context.exception.code, case["expected_error"])
                else:
                    validate_media_mime(source)



    def test_validate_media_file(self):
        cases = mv_cases.validate_media_file_test_cases
        for case_name, case in cases.items():
            with self.subTest(case=case_name):
                if case["expected_error"]:
                    source_path = case["filepath"].format(filepath = self.test_corrupted_filepath)
                else:
                    source_path = case["filepath"].format(filepath = self.test_video_filepath)

                if case["expected_error"]:
                    with self.assertRaises(AppError) as context:
                        validate_media_file(source_path)

                    self.assertEqual(context.exception.code, case["expected_error"])
                else:
                    validate_media_file(source_path)



    def test_validate_language(self):
        cases = mv_cases.validate_language_test_cases
        for case_name, case in cases.items():
            with self.subTest(case=case_name):
                expected = case.get("expected")
                expected_error = case.get("expected_error")

                if expected:
                    self.assertEqual(expected, validate_language(case["input"]))
                if expected_error:
                    with self.assertRaises(AppError) as context:
                        validate_language(case["input"])

                    self.assertEqual(context.exception.code, expected_error)




#python -m unittest discover -s tests -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "test_media_validation.py" -v
