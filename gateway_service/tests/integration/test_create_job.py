"""
test_create_job.py

Tests for the /jobs endpoint.
"""

import pytest
from tests.integration.data.gateway_file_test_cases import reference_endpoint_test_cases as cases 

import tests.shared_helpers.testing_constants as tc
import tests.shared_helpers.models as models
import os
import requests
from tests.integration.helpers.utils import create_microservices_mocks
import copy


def test_200_case(client, settings, mock_pipeline_clients):
    """"
    Happy path: successful transcribing
    """
    
    case = cases.get("valid_reference")
    json_data = copy.deepcopy(case["request_json"])
    downloader_file_path = None
    if "source" in json_data:
        json_data["source"] = os.path.join(
            settings.TEST_FOLDER,
            json_data["source"]
        )
        downloader_file_path=json_data["source"]
    create_microservices_mocks(mock_pipeline_clients, downloader_file_path=downloader_file_path)
    response = client.post("/jobs", json=json_data)

    assert response.status_code == case["expected_status_code"] 
    response_json = response.json()
    response_model = models.PostResponseData(**response_json)
    assert response_model.data.result_url == tc.TEST_TRANSCRIBE_PATH


@pytest.mark.parametrize("case_name, testing_case", cases.items())
def test_post_errors(client, case_name, testing_case, settings, mock_pipeline_clients):
    if case_name != "valid_reference":
        json_data = testing_case.get("request_json")
        downloader_file_path = None
        if "source" in json_data:
            json_data["source"] = os.path.join(
                settings.TEST_FOLDER,
                json_data["source"]
            )
            downloader_file_path=json_data["source"]
        mock_pipeline_error = testing_case.get("mock_pipeline_error")
        if mock_pipeline_error == "CONNECTION_ERROR":
            create_microservices_mocks(mock_pipeline_clients, 
                        downloader_file_path=downloader_file_path,
                        downloader_side_effect=requests.exceptions.ConnectionError())
        else:
            create_microservices_mocks(mock_pipeline_clients)

        response = client.post(
            "/jobs",
            json=json_data
        )

        
        assert response.status_code == testing_case["expected_status_code"] 
        response_json = response.json()
        response_model = models.Message(**response_json)
        assert response_model.code == testing_case["expected_error_code"]         

        
                                                            
#pytest tests/integration/test_create_job.py -v
#pytest tests/integration/test_create_job.py::test_200_case -v


