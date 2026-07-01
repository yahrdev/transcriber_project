"""
utils.py

Helper functions for integration tests: API calls, dummy file preparation,
test case loading, and common assertions.
"""

from flask.wrappers import Response
import tests.shared_helpers.dummy_generators as dg
from tests.integration.data.convert_file_test_cases import testing_data
import os

def convert_file_endpoint(client, **kwargs) -> Response:
    """
    Sends a request to the /convert endpoint
    """

    json_data = convert_file_payload(
        kwargs["file_path"],
        kwargs["target_filename"],
        kwargs["source_extension"],
        kwargs["target_extension"]
    )
    route = kwargs.get("route") or "/convert"
    return client.post(route, json=json_data)


def convert_file_payload(file_path: str, target_filename: str, source_extension: str, target_extension: str) -> dict:
    return {
        "file_path": file_path,
        "target_filename": target_filename,
        "source_extension": source_extension,
        "target_extension": target_extension
    }





def create_dummy_file(path):
    """
    The function for generating dummy files used in tests (e.g., video, text, PDF).
    """

    ext = os.path.splitext(path)[1].lstrip(".").lower()
    if ext in {"mp4", "avi", "webm", "mov", "mkv"}:
        dg.create_dummy_video(path)


def get_case(name: str) -> dict:
    """
    Retrieves a specific test case by name
    """

    return next(c for c in testing_data if c["name"] == name)

def prepare_case_input(settings, case: dict):
    """
    Prepares input and expected output filename for a test case
    """

    json_data = case["data"]
    input_filename = json_data["filename_with_ext"]
    input_path = os.path.join(settings.TEST_FOLDER, input_filename)
    target_filename_with_ext = f"{json_data['target_filename']}.{json_data['target_extension']}"

    kwargs = {
    "file_path": input_path,
    "target_filename": json_data["target_filename"],
    "source_extension": json_data["source_extension"],
    "target_extension": json_data["target_extension"],
    "route": case["route"]
    }

    return kwargs, target_filename_with_ext


def assert_error_response(response, expected_status: int, expected_code: str):
    """
    Asserts error response status and error code
    """

    assert response.status_code == expected_status
    data = response.get_json()
    assert data["code"] == expected_code


def prepare_wrong_type(file_path: str):
    """
    Used to mark a test case as skipped in test parametrization
    """

    with open(file_path, "w") as f:
            f.write("Some test content")

def prepare_folder(folder_path: str):
    """
    Creates a folder without file inside
    """

    os.makedirs(folder_path, exist_ok=True)


def skip_case(_=None):
    """
    For test skipping
    """
    
    return "SKIP"
