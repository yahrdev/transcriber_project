"""
test_web_ui_routes.py

Integration tests for web_ui_service routes.
"""

from io import BytesIO
from unittest.mock import Mock, patch

from app.exceptions.exceptions import MicroserviceError


def test_index_success(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Video Transcriber" in response.data
    assert b"Start transcription" in response.data
    assert b"Language" in response.data


def test_upload_without_file(client):
    response = client.post(
        "/upload",
        data={
            "client_id": "web-ui",
            "language": "uk",
        }
    )

    assert response.status_code == 400
    assert b"No file uploaded" in response.data


def test_upload_success(client):
    with patch("app.routers.gc.post_file") as mock_post_file:
        mock_post_file.return_value = "test-job-id"

        response = client.post(
            "/upload",
            data={
                "client_id": "web-ui",
                "language": "uk",
                "file": (BytesIO(b"fake video content"), "test.mp4"),
            },
            content_type="multipart/form-data"
        )

        assert response.status_code == 200
        assert b"Transcription completed" in response.data
        assert b"/download/test-job-id" in response.data

        mock_post_file.assert_called_once()


def test_upload_gateway_error(client):
    with patch("app.routers.gc.post_file") as mock_post_file:
        mock_post_file.side_effect = MicroserviceError(
            service="gateway",
            upstream_status_code=None,
            upstream_error_code="CONNECTION_ERROR",
            upstream_error_message="Connection refused",
            upstream_request={}
        )

        response = client.post(
            "/upload",
            data={
                "client_id": "web-ui",
                "language": "uk",
                "file": (BytesIO(b"fake video content"), "test.mp4"),
            },
            content_type="multipart/form-data"
        )

        assert response.status_code == 500
        assert response.json["code"] == "INTERNAL_ERROR"


def test_download_success(client):
    with patch("app.routers.gc.get_file") as mock_get_file:
        gateway_response = Mock()
        gateway_response.content = b"transcription text"
        gateway_response.status_code = 200
        gateway_response.headers = {
            "content-type": "text/plain",
            "content-disposition": 'attachment; filename="result.txt"'
        }

        mock_get_file.return_value = gateway_response

        response = client.get("/download/test-job-id")

        assert response.status_code == 200
        assert response.data == b"transcription text"
        assert response.content_type == "text/plain"
        assert "attachment" in response.headers["Content-Disposition"]
        assert "result.txt" in response.headers["Content-Disposition"]

        mock_get_file.assert_called_once()



    #pytest tests/integration -v