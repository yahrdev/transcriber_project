"""
test_connections.py

Unit tests for connections.py
"""

import unittest
from tests.testing_settings import TestSettings
from app.exceptions.exceptions import  MicroserviceError, AppError
from app.microservices.connections import create_and_post
from tests.unit.data import connections_test_cases as c_cases
from app.models.micro_schemas import DownloaderResponseData, DownloaderSourceData, AuthNone
from unittest.mock import patch, Mock
import requests
from json import JSONDecodeError


class TestConnections(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()
        self.data =  DownloaderSourceData(source_type="path", 
                                source="test", 
                                auth=AuthNone(method="none"))

    def tearDown(self):
        pass

    def CreateMock(self, mock_post, 
                   status_code = None, 
                   return_value = None, 
                   ok = None, 
                   side_effect = None,
                   response_side_effect = None):
        
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.ok = ok
        mock_response.json.return_value = return_value
        mock_post.return_value = mock_response
        mock_post.side_effect = side_effect
        mock_response.json.side_effect = response_side_effect



    def test_create_and_post_success(self):
        case = c_cases.connections_success_case
        with patch("app.microservices.connections.requests.post") as mock_post:
            expected_response = case["response_json"]
            self.CreateMock( mock_post, 
                   status_code = case["response_status_code"], 
                   return_value = expected_response, 
                   ok = True)
            
            result = create_and_post(self.data, 
                                    DownloaderResponseData,
                                    self.settings.downloader_url,
                                    "downloader_service")
            self.assertIsInstance(result, DownloaderResponseData)
            self.assertEqual(result.file_path, expected_response["file_path"])
            self.assertEqual(result.file_name, expected_response["file_name"])
            self.assertEqual(result.file_extension, expected_response["file_extension"])


    def test_create_and_post_connection_error(self):
        case = c_cases.connections_microservice_unavailable_case
        with patch("app.microservices.connections.requests.post") as mock_post:
            self.CreateMock( mock_post, 
                   status_code = case["response_status_code"],
                   side_effect=requests.exceptions.ConnectionError(),  
                   ok = False)

            with self.assertRaises(MicroserviceError) as context:
                create_and_post(self.data, 
                                DownloaderResponseData,
                                self.settings.downloader_url,
                                "downloader_service")
            self.assertEqual(context.exception.upstream_error_code, case["expected_error"])




    def test_create_and_post_wrong_responses(self):
        cases = c_cases.connections_wrong_responses_cases
        for case_name, case in cases.items():
            with self.subTest(case=case_name):
                with patch("app.microservices.connections.requests.post") as mock_post:
                    if case["response_json"] is not None:
                        self.CreateMock( mock_post, 
                            status_code = case["response_status_code"], 
                            return_value = case["response_json"], 
                            ok = True)
                    else:
                        self.CreateMock( mock_post, 
                            status_code = case["response_status_code"], 
                            response_side_effect = JSONDecodeError("Invalid JSON", "", 0),
                            ok = True)

                    with self.assertRaises(MicroserviceError) as context:
                        create_and_post(self.data, 
                                        DownloaderResponseData,
                                        self.settings.downloader_url,
                                        "downloader_service")
                    self.assertEqual(context.exception.upstream_error_code, case["expected_error"])
                        



    def test_create_and_post_upstream_error(self):
        cases = c_cases.connections_upstream_errors_cases
        for case_name, case in cases.items():
            with self.subTest(case=case_name):
                with patch("app.microservices.connections.requests.post") as mock_post:
                    self.CreateMock(mock_post, 
                        status_code = case["response_status_code"], 
                        return_value = case["response_json"], 
                        ok = False)
                    
                    with self.assertRaises(MicroserviceError) as context:
                        create_and_post(self.data, 
                                        DownloaderResponseData,
                                        self.settings.downloader_url,
                                        "downloader_service")
                    
                    self.assertEqual(context.exception.upstream_error_code, case["upstream_error_code"])
                    self.assertEqual(context.exception.code, case["expected_error_code"])


    def test_create_and_post_wrong_error(self):
        case = c_cases.connections_wrong_error_response_case
        with patch("app.microservices.connections.requests.post") as mock_post:
            self.CreateMock(mock_post, 
                        status_code = case["response_status_code"], 
                        return_value = case["response_json"], 
                        ok = False)

            with self.assertRaises(MicroserviceError) as context:
                create_and_post(self.data, 
                                DownloaderResponseData,
                                self.settings.downloader_url,
                                "downloader_service")
            self.assertEqual(context.exception.upstream_error_code, case["expected_error"])
                    



#python -m unittest discover -s tests -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "*.py" -v 
#python -m unittest discover -s tests/unit -p "test_connections.py" -v
#python -m unittest tests.unit.test_connections.TestConnections.test_create_and_post_wrong_responses
