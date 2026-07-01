"""
test_download_file.py

Tests for the /download endpoint.
"""

import pytest
from tests.integration.data.download_file_test_cases import testing_data
from unittest.mock import patch
from tests.integration.helpers.utils import (
                            download_file_endpoint,
                            get_case,
                            prepare_case_input
                        )

from tests.shared_helpers.models import ResponseData, Message
from typing import Union
import os


def test_200_case(client, settings):
    """"
    Happy path: successful downloading
    """
    
    testing_case = get_case("test_200_case")

    
    correct_response: Union[ResponseData, Message]
    request, correct_response, route, status_code = prepare_case_input(testing_case)

    response = download_file_endpoint(client, route, request=request)
    
    assert response.status_code == status_code
    data = response.json()
    assert data["file_name"]
    assert data["file_extension"] == correct_response.file_extension
    path_normalized = os.path.normpath(data["file_path"])
    tempdir_normalized = os.path.normpath(settings.TEMP_DIR_OUTPUT)
    #check the longest the same start
    assert os.path.commonpath([path_normalized, tempdir_normalized]) == tempdir_normalized 
   


@pytest.mark.parametrize("testing_case", testing_data, ids=[c["name"] for c in testing_data])
def test_wrong_cases(client, testing_case):
    """
    Unhappy paths: tests various error scenarios
    """

    if testing_case["name"] in ["test_200_case", "test_internal_error"]:
        pytest.skip(f"Skipping test {testing_case['name']}") #because we consider them in separate functions
        
    
    correct_response: Union[ResponseData, Message]
    request, correct_response, route, status_code = prepare_case_input(testing_case)
    

    response = download_file_endpoint(client, route, request=request)
    assert response.status_code == status_code
    data = response.json()
    assert data["code"] == correct_response.code




def test_internal_error(client):
    """
     Simulates internal error during downloading
    """

    testing_case = get_case("test_internal_error")
    correct_response: Union[ResponseData, Message]
    request, correct_response, route, status_code = prepare_case_input(testing_case)


    # replace get_extractor() with a fake function
    with patch("app.api.routers.get_extractor") as mock_get: 
        mock_downloader = mock_get.return_value
        mock_downloader.extract.side_effect = Exception("Simulated crash")
        response = download_file_endpoint(client, route, request=request)

    assert response.status_code == status_code
    data = response.json()
    assert data["code"] == correct_response.code

#pytest tests/integration/test_download_file.py -v


