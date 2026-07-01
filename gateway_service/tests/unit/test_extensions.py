"""
test_extensions.py

Unit tests for extensions.py
"""

import unittest
from app.exceptions.exceptions import AppError
from app.utils.extensions import extract_extension
from tests.unit.data import extensions_test_cases as e_cases


class TestExtensions(unittest.TestCase):


    def test_extract_extension(self):
        cases = e_cases.extension_test_cases
        for case_name, case in cases.items():
            with self.subTest(case=case_name):
                expected = case.get("expected")
                expected_error = case.get("expected_error")

                if expected:
                    self.assertEqual(expected, extract_extension(case["filename"]))
                if expected_error:
                    with self.assertRaises(AppError) as context:
                        extract_extension(case["filename"])

                    self.assertEqual(context.exception.code, expected_error)




#python -m unittest discover -s tests -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "test_extensions.py" -v
