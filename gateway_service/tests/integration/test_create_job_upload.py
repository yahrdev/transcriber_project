"""
test_create_job_upload.py

Tests for the /jobs endpoint.
"""

import pytest
from tests.integration.data.gateway_file_test_cases import upload_endpoint_test_cases as cases 
import tests.shared_helpers.testing_constants as tc
import tests.shared_helpers.models as models
import os
import mimetypes
import requests
from tests.integration.helpers.utils import create_microservices_mocks


def test_200_case(client, settings, mock_pipeline_clients):
    """"
    Happy path: successful transcribing
    """
    
    create_microservices_mocks(mock_pipeline_clients)
    case = cases.get("valid_upload")
    client_id = "123"
    language = case.get("language")
    disk_file = case.get("disk_file")
    filename = case.get("upload_filename")
    test_file_path = os.path.join(
                                    settings.TEST_FOLDER,
                                    disk_file
                                )
    content_type = mimetypes.guess_type(test_file_path)[0]


    with open(test_file_path, "rb") as f:
        response = client.post("/jobs/upload", data={
                                                    "client_id": client_id,
                                                    "language": language,
                                                                        },
                                                                        files={
                                                                            "file": (filename, f, content_type)
                                                                        }
                                
                            )    
    assert response.status_code == case["expected_status_code"] 
    response_json = response.json()
    response_model = models.PostResponseData(**response_json)
    assert response_model.data.result_url == tc.TEST_TRANSCRIBE_PATH


@pytest.mark.parametrize("case_name, testing_case", cases.items())
def test_post_upload_errors(client, case_name, testing_case, settings, mock_pipeline_clients):
    if case_name != "valid_upload":
        
        mock_pipeline_error = testing_case.get("mock_pipeline_error")
        if mock_pipeline_error == "CONNECTION_ERROR":
            create_microservices_mocks(mock_pipeline_clients, 
                                       converter_side_effect=requests.exceptions.ConnectionError())
        else:
            create_microservices_mocks(mock_pipeline_clients)
        client_id = "123"
        language = testing_case.get("language")
        disk_file = testing_case.get("disk_file")
        filename = testing_case.get("upload_filename")
        if filename:
            test_file_path = os.path.join(
                                            settings.TEST_FOLDER,
                                            disk_file
                                        )
        else:
            test_file_path = ""
        content_type = mimetypes.guess_type(test_file_path)[0]

        with open(test_file_path, "rb") as f:
            response = client.post("/jobs/upload", data={
                                                        "client_id": client_id,
                                                        "language": language,
                                                                            },
                                                                            files={
                                                                                "file": (filename, f, content_type)
                                                                            }
                                
                    )        
        assert response.status_code == testing_case["expected_status_code"] 
        response_json = response.json()
        response_model = models.Message(**response_json)
        assert response_model.code == testing_case["expected_error_code"]         

        
                                                            
#pytest tests/integration/test_create_job_upload.py -v
#pytest tests/integration/test_create_job_upload.py::test_200_case -v


