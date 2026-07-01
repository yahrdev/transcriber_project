"""
test_get_job.py

Tests for the "/jobs/{job_id}/result/download" endpoint.
"""


from tests.integration.data.gateway_file_test_cases import reference_endpoint_test_cases as post_cases 
from tests.integration.data.gateway_file_test_cases import download_result_endpoint_test_cases as get_cases
import tests.shared_helpers.testing_constants as tc
import tests.shared_helpers.models as models
import os
from tests.integration.helpers.utils import create_microservices_mocks
import copy



def test_200_case_download(client, settings, mock_pipeline_clients):
    """"
    Happy path: successful transcribing
    """
    
    post_case = post_cases.get("valid_reference")
    json_data = copy.deepcopy(post_case["request_json"])
    downloader_file_path = None
    if "source" in json_data:
        json_data["source"] = os.path.join(
            settings.TEST_FOLDER,
            json_data["source"]
        )
        downloader_file_path=json_data["source"]
    get_case = get_cases.get("completed_job_existing_file")
    transcriber_file_path = None
    if "result_disk_file" in get_case:
        transcriber_file_path = os.path.join(
            settings.TEST_FOLDER,
            get_case["result_disk_file"])
    create_microservices_mocks(mock_pipeline_clients, 
                 downloader_file_path=downloader_file_path,
                 transcriber_file_path = transcriber_file_path)
    response = client.post("/jobs", json=json_data)

    response_json = response.json()
    response_model = models.PostResponseData(**response_json)
    url = "/jobs/{job_id}/result/download".format(job_id = response_model.job_id)

    

    response = client.get(url=url)
    assert response.status_code == get_case["expected_status_code"]
    assert response.headers["content-type"].startswith(get_case["expected_content_type"])
    with open(response_model.data.result_url, "r", encoding="utf-8") as f:
        expected_text = f.read()
    assert expected_text[:10] in response.text




def test_get_wrong_job_download(client):

    get_case = get_cases.get("job_not_found")

    url = "/jobs/{job_id}/result/download".format(job_id = get_case["job_id"])

    response = client.get(url=url)
    assert response.status_code == get_case["expected_status_code"] 
    response_json = response.json()
    response_model = models.Message(**response_json)
    assert response_model.code == get_case["expected_error_code"] 


def test_200_case_status(client, settings, mock_pipeline_clients):
    """"
    Happy path: successful transcribing
    """
    
    post_case = post_cases.get("valid_reference")
    json_data = copy.deepcopy(post_case["request_json"])
    downloader_file_path = None
    if "source" in json_data:
        json_data["source"] = os.path.join(
            settings.TEST_FOLDER,
            json_data["source"]
        )
        downloader_file_path=json_data["source"]
    get_case = get_cases.get("completed_job_existing_file")
    transcriber_file_path = None
    if "result_disk_file" in get_case:
        transcriber_file_path = os.path.join(
            settings.TEST_FOLDER,
            get_case["result_disk_file"])
    create_microservices_mocks(mock_pipeline_clients, 
                 downloader_file_path=downloader_file_path,
                 transcriber_file_path = transcriber_file_path)
    response = client.post("/jobs", json=json_data)

    response_json = response.json()
    response_model = models.PostResponseData(**response_json)
    url = "/jobs/{job_id}/status".format(job_id = response_model.job_id)

    

    response = client.get(url=url)
    assert response.status_code == get_case["expected_status_code"]
    response_json = response.json()
    response_model = models.ResponseStatusModel(**response_json)
    assert response_model.status == "completed"




def test_get_wrong_job_status(client):

    get_case = get_cases.get("job_not_found")

    url = "/jobs/{job_id}/status".format(job_id = get_case["job_id"])

    response = client.get(url=url)
    assert response.status_code == get_case["expected_status_code"] 
    response_json = response.json()
    response_model = models.Message(**response_json)
    assert response_model.code == get_case["expected_error_code"] 

        
                                                            
#pytest tests/integration/test_get_job.py -v
#pytest tests/integration/test_get_job.py::test_200_case -v


