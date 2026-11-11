"""
test_create_job_upload.py

Tests for the POST /jobs/upload endpoint.
"""

import mimetypes
import os

import pytest
import requests

from tests.integration.data.gateway_file_test_cases import upload_endpoint_test_cases as cases
from tests.integration.helpers.utils import create_microservices_mocks
import tests.shared_helpers.models as models


def post_upload(client, settings, case):
    """Sends the file described in the test case to POST /jobs/upload."""
    test_file_path = os.path.join(settings.TEST_FOLDER, case.get("disk_file"))
    content_type = mimetypes.guess_type(test_file_path)[0]

    with open(test_file_path, "rb") as f:
        return client.post("/jobs/upload",
                           data={"client_id": "123", "language": case.get("language")},
                           files={"file": (case.get("upload_filename"), f, content_type)})


def test_202_case(client, settings, mock_pipeline_clients, queued_tasks):
    """
    Happy path: the file is accepted and the job is put in the queue.
    """
    create_microservices_mocks(mock_pipeline_clients)
    case = cases.get("valid_upload")

    response = post_upload(client, settings, case)

    assert response.status_code == case["expected_status_code"]
    response_model = models.PostResponseData(**response.json())
    assert response_model.data is None

    upload_delay, _ = queued_tasks
    upload_delay.assert_called_once()
    assert upload_delay.call_args.kwargs["job_id"] == str(response_model.job_id)

    status = client.get(f"/jobs/{response_model.job_id}/status").json()
    assert status["status"] == "pending"


@pytest.mark.parametrize("case_name, testing_case", cases.items())
def test_post_upload_errors(client, case_name, testing_case, settings, mock_pipeline_clients, queued_tasks):
    """
    Validation errors are returned by the API immediately; nothing is put in the queue.
    """
    if case_name == "valid_upload":
        pytest.skip("happy path is tested separately")

    create_microservices_mocks(mock_pipeline_clients)

    response = post_upload(client, settings, testing_case)

    assert response.status_code == testing_case["expected_status_code"]
    response_model = models.Message(**response.json())
    assert response_model.code == testing_case["expected_error_code"]

    upload_delay, _ = queued_tasks
    upload_delay.assert_not_called()


def test_worker_error(client, settings, mock_pipeline_clients, inline_tasks):
    """
    The converter fails inside the worker: the API still answers 202,
    the error is visible only through the job status.
    """
    create_microservices_mocks(mock_pipeline_clients,
                               converter_side_effect=requests.exceptions.ConnectionError())

    response = post_upload(client, settings, cases.get("valid_upload"))

    assert response.status_code == 202
    job_id = response.json()["job_id"]
    assert client.get(f"/jobs/{job_id}/status").json()["status"] == "failed"


# pytest tests/integration/test_create_job_upload.py -v