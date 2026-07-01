"""
test_gateway_client.py

Unit tests for gateway_client.py.
"""

import unittest
from unittest.mock import patch, Mock
import requests

from app.backend_service import gateway_client as gc
from app.exceptions.exceptions import MicroserviceError
from tests.testing_settings import TestSettings


class TestGatewayClient(unittest.TestCase):

    def setUp(self):
        self.settings = TestSettings.generate()

    def create_mock_response(
        self,
        mock_request,
        status_code=200,
        ok=True,
        json_data=None,
        json_side_effect=None,
        content=b"test file",
        headers=None,
    ):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.ok = ok
        mock_response.content = content
        mock_response.headers = headers or {}
        mock_response.json.return_value = json_data
        mock_response.json.side_effect = json_side_effect
        mock_request.return_value = mock_response
        return mock_response

    def test_post_file_success(self):
        with patch("app.backend_service.gateway_client.requests.post") as mock_post:
            self.create_mock_response(
                mock_post,
                status_code=200,
                ok=True,
                json_data={
                    "job_id": "550e8400-e29b-41d4-a716-446655440000",
                    "data": None
                }
            )

            result = gc.post_file(
                settings=self.settings,
                client_id="web-ui",
                language="uk",
                filename="test.mp4",
                file=b"fake file",
                content_type="video/mp4"
            )

            self.assertEqual(
                str(result),
                "550e8400-e29b-41d4-a716-446655440000"
            )
            mock_post.assert_called_once()

    def test_post_file_connection_error(self):
        with patch("app.backend_service.gateway_client.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError()

            with self.assertRaises(MicroserviceError) as context:
                gc.post_file(
                    settings=self.settings,
                    client_id="web-ui",
                    language="uk",
                    filename="test.mp4",
                    file=b"fake file",
                    content_type="video/mp4"
                )

            self.assertEqual(
                context.exception.upstream_error_code,
                "CONNECTION_ERROR"
            )

    def test_post_file_invalid_json_response(self):
        with patch("app.backend_service.gateway_client.requests.post") as mock_post:
            self.create_mock_response(
                mock_post,
                status_code=200,
                ok=True,
                json_side_effect=ValueError("Invalid JSON")
            )

            with self.assertRaises(MicroserviceError) as context:
                gc.post_file(
                    settings=self.settings,
                    client_id="web-ui",
                    language="uk",
                    filename="test.mp4",
                    file=b"fake file",
                    content_type="video/mp4"
                )

            self.assertEqual(
                context.exception.upstream_error_code,
                "INVALID_JSON_RESPONSE"
            )

    def test_post_file_invalid_success_schema(self):
        with patch("app.backend_service.gateway_client.requests.post") as mock_post:
            self.create_mock_response(
                mock_post,
                status_code=200,
                ok=True,
                json_data={"wrong_field": "wrong"}
            )

            with self.assertRaises(MicroserviceError) as context:
                gc.post_file(
                    settings=self.settings,
                    client_id="web-ui",
                    language="uk",
                    filename="test.mp4",
                    file=b"fake file",
                    content_type="video/mp4"
                )

            self.assertEqual(
                context.exception.upstream_error_code,
                "RESPONSE_VALIDATION_ERROR"
            )

    def test_post_file_upstream_error(self):
        with patch("app.backend_service.gateway_client.requests.post") as mock_post:
            self.create_mock_response(
                mock_post,
                status_code=400,
                ok=False,
                json_data={
                    "message": "Invalid file",
                    "code": "INVALID_FILE_EXTENSION"
                }
            )

            with self.assertRaises(MicroserviceError) as context:
                gc.post_file(
                    settings=self.settings,
                    client_id="web-ui",
                    language="uk",
                    filename="test.exe",
                    file=b"fake file",
                    content_type="application/octet-stream"
                )

            self.assertEqual(
                context.exception.upstream_error_code,
                "INVALID_FILE_EXTENSION"
            )

    def test_get_file_success(self):
        with patch("app.backend_service.gateway_client.requests.get") as mock_get:
            mock_response = self.create_mock_response(
                mock_get,
                status_code=200,
                ok=True,
                content=b"transcription text",
                headers={
                    "content-type": "text/plain",
                    "content-disposition": 'attachment; filename="result.txt"'
                }
            )

            result = gc.get_file(
                settings=self.settings,
                job_id="550e8400-e29b-41d4-a716-446655440000"
            )

            self.assertEqual(result, mock_response)
            self.assertEqual(result.content, b"transcription text")