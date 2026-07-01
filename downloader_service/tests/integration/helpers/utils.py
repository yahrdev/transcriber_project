"""
utils.py

Helper functions for integration tests: API calls, dummy file preparation,
test case loading, and common assertions.
"""


import tests.shared_helpers.models as m
from tests.integration.data.download_file_test_cases import testing_data

def download_file_endpoint(client, route, request: m.SourceData):
    """
    Sends a request to the /download
    """
    json_data = request.model_dump()

    return client.post(route, json=json_data)



def get_case(name: str) -> dict:
    """
    Retrieves a specific test case by name
    """

    return next(c for c in testing_data if c["name"] == name)

def prepare_case_input(case: dict):
    """
    Prepares both the request object and the expected response object
    from a single test case dictionary.
    """
    status_code = case["status_code"]
    json_data = case["data"]
    auth_data = json_data["auth"]
    auth = m.AuthNone(method=auth_data["method"])
    request = m.SourceData(source_type=json_data["source_type"],
                        source=json_data["source"],
                        auth=auth)
    
    
    json_data = case["expected_response"]
    
    if json_data.get("file_path"):
        response = m.ResponseData(file_path=json_data["file_path"],
                                 file_name=json_data["file_name"],
                                 file_extension=json_data["file_extension"]
                               )
    elif json_data.get("message"):
        response = m.Message(message=json_data["message"],
                            code=json_data["code"])
    else:
        raise ValueError(f"Unknown expected_response shape: {json_data}")


    route = case["route"]

    return request, response, route, status_code

