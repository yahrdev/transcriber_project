"""
test_create_job.py

Tests for the POST /jobs endpoint.
"""

import copy
import os

import pytest
import requests

from tests.integration.data.gateway_file_test_cases import reference_endpoint_test_cases as cases
from tests.integration.helpers.utils import create_microservices_mocks
import tests.shared_helpers.models as models


def build_reference_json(case, settings):
    json_data = copy.deepcopy(case["request_json"])
    if "source" in json_data:
        json_data["source"] = os.path.join(settings.TEST_FOLDER, json_data["source"])
    return json_data


def test_202_case(client, settings, mock_pipeline_clients, queued_tasks):
    """
    Happy path: the job is accepted and put in the queue, the result is not ready yet.
    """
    case = cases.get("valid_reference")
    json_data = build_reference_json(case, settings)
    create_microservices_mocks(mock_pipeline_clients, downloader_file_path=json_data["source"])

    response = client.post("/jobs", json=json_data)

    assert response.status_code == case["expected_status_code"]
    response_model = models.PostResponseData(**response.json())
    assert response_model.data is None

    _, reference_delay = queued_tasks
    reference_delay.assert_called_once()
    assert reference_delay.call_args.kwargs["job_id"] == str(response_model.job_id)

    status = client.get(f"/jobs/{response_model.job_id}/status").json()
    assert status["status"] == "pending"


@pytest.mark.parametrize("case_name, testing_case", cases.items())
def test_post_errors(client, case_name, testing_case, settings, mock_pipeline_clients, queued_tasks):
    """
    Validation errors are returned by the API immediately; nothing is put in the queue.
    """
    if case_name == "valid_reference":
        pytest.skip("happy path is tested separately")

    json_data = build_reference_json(testing_case, settings)
    create_microservices_mocks(mock_pipeline_clients)

    response = client.post("/jobs", json=json_data)

    assert response.status_code == testing_case["expected_status_code"]
    response_model = models.Message(**response.json())
    assert response_model.code == testing_case["expected_error_code"]

    _, reference_delay = queued_tasks
    reference_delay.assert_not_called()


def test_worker_error(client, settings, mock_pipeline_clients, inline_tasks):
    """
    The downloader fails inside the worker: the API still answers 202,
    the error is visible only through the job status.
    """
    case = cases.get("valid_reference")
    json_data = build_reference_json(case, settings)
    create_microservices_mocks(mock_pipeline_clients,
                               downloader_file_path=json_data["source"],
                               downloader_side_effect=requests.exceptions.ConnectionError())

    response = client.post("/jobs", json=json_data)

    assert response.status_code == 202
    job_id = response.json()["job_id"]
    assert client.get(f"/jobs/{job_id}/status").json()["status"] == "failed"


# pytest tests/integration/test_create_job.py -v