"""
test_get_job.py

Tests for GET /jobs/{job_id}/status and GET /jobs/{job_id}/result/download.
"""

import copy
import os

import requests

from tests.integration.data.gateway_file_test_cases import reference_endpoint_test_cases as post_cases
from tests.integration.data.gateway_file_test_cases import download_result_endpoint_test_cases as get_cases
from tests.integration.helpers.utils import create_microservices_mocks
import tests.shared_helpers.models as models


def create_job(client, settings, mock_pipeline_clients, downloader_side_effect=None):
    """Creates a job through POST /jobs. Returns (job_id, path of the expected result file)."""
    json_data = copy.deepcopy(post_cases["valid_reference"]["request_json"])
    json_data["source"] = os.path.join(settings.TEST_FOLDER, json_data["source"])
    result_path = os.path.join(settings.TEST_FOLDER,
                               get_cases["completed_job_existing_file"]["result_disk_file"])

    create_microservices_mocks(mock_pipeline_clients,
                               downloader_file_path=json_data["source"],
                               downloader_side_effect=downloader_side_effect,
                               transcriber_file_path=result_path)

    response = client.post("/jobs", json=json_data)
    assert response.status_code == 202
    return response.json()["job_id"], result_path


def assert_error(response, case):
    assert response.status_code == case["expected_status_code"]
    response_model = models.Message(**response.json())
    assert response_model.code == case["expected_error_code"]


# ---------- download ----------

def test_200_case_download(client, settings, mock_pipeline_clients, inline_tasks):
    """The worker has finished: the file is returned."""
    case = get_cases["completed_job_existing_file"]
    job_id, result_path = create_job(client, settings, mock_pipeline_clients)

    response = client.get(f"/jobs/{job_id}/result/download")

    assert response.status_code == case["expected_status_code"]
    assert response.headers["content-type"].startswith(case["expected_content_type"])
    with open(result_path, "r", encoding="utf-8") as f:
        expected_text = f.read()
    assert expected_text[:10] in response.text


def test_409_download_not_finished(client, settings, mock_pipeline_clients):
    """The job is still in the queue: 409 NOT_FINISHED instead of 500."""
    job_id, _ = create_job(client, settings, mock_pipeline_clients)

    response = client.get(f"/jobs/{job_id}/result/download")

    assert_error(response, get_cases["job_not_finished"])


def test_409_download_failed(client, settings, mock_pipeline_clients, inline_tasks):
    """The job failed in the worker: 409 JOB_FAILED."""
    job_id, _ = create_job(client, settings, mock_pipeline_clients,
                           downloader_side_effect=requests.exceptions.ConnectionError())

    response = client.get(f"/jobs/{job_id}/result/download")

    assert_error(response, get_cases["job_failed"])


def test_get_wrong_job_download(client):
    case = get_cases["job_not_found"]
    response = client.get(f"/jobs/{case['job_id']}/result/download")
    assert_error(response, case)


# ---------- status ----------

def test_status_pending(client, settings, mock_pipeline_clients):
    """Right after POST the job waits in the queue."""
    job_id, _ = create_job(client, settings, mock_pipeline_clients)

    response = client.get(f"/jobs/{job_id}/status")

    assert response.status_code == 200
    assert response.json()["status"] == "pending"


def test_status_completed(client, settings, mock_pipeline_clients, inline_tasks):
    """After the worker has finished the status is 'completed'."""
    job_id, _ = create_job(client, settings, mock_pipeline_clients)

    response = client.get(f"/jobs/{job_id}/status")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_get_wrong_job_status(client):
    case = get_cases["job_not_found"]
    response = client.get(f"/jobs/{case['job_id']}/status")
    assert_error(response, case)


# pytest tests/integration/test_get_job.py -v