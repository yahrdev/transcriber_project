"""
utils.py

Helper functions for integration tests: API calls, dummy file preparation,
test case loading, and common assertions.
"""


import tests.shared_helpers.models as m
from tests.integration.data.transcribe_file_test_cases import internal_error_testing_data
import os

def transcribe_file_endpoint(client, route, request):
    """
    Sends a request to the /transcribe_file
    """
    if isinstance(request, m.SourceData):
        json_data = request.model_dump()
        return client.post(route, json=json_data)
    else:
        data = request
        return client.post(route, data=data)


def prepare_case_input(case: dict, test_dir: str, output_dir: str):
    """
    Prepares both the request object and the expected response object
    from a single test case dictionary.
    """
    status_code = case["status_code"]
    json_data = case["data"]
    file_name = None
    if isinstance(json_data, dict):
        if json_data.get("file_name"):
            file_name=json_data["file_name"]
        if json_data.get("file_path"):
            json_data["file_path"] = os.path.join(test_dir, json_data["file_path"])

        request = m.SourceData(**json_data)
    else:
        request = json_data
    
    json_data = case["expected_response"]
    
    if json_data.get("file_path"):
        response = m.ResponseData(file_path=json_data["file_path"].format(
                                TEMP_DIR_OUTPUT=output_dir,
                                file_name=file_name))
    elif json_data.get("message"):
        response = m.Message(message=json_data["message"],
                            code=json_data["code"])
    else:
        raise ValueError(f"Unknown expected_response shape: {json_data}")


    route = case["route"]

    return request, response, route, status_code

