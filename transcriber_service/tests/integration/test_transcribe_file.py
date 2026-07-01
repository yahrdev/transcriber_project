"""
test_transcribe_file.py

Tests for the /transcribe endpoint.
"""

import pytest
import tests.integration.data.transcribe_file_test_cases as td
from unittest.mock import patch
from tests.integration.helpers.utils import (
                            transcribe_file_endpoint,
                            prepare_case_input
                        )

from tests.shared_helpers.models import ResponseData, Message
from typing import Union
import os

@pytest.mark.parametrize("testing_case", td.success_testing_data, ids=[c["name"] for c in td.success_testing_data])
def test_200_case(client, testing_case, settings):
    """"
    Happy path: successful transcibing
    """

    correct_response: Union[ResponseData, Message]
    request, correct_response, route, status_code = prepare_case_input(testing_case, 
                                                                       settings.TEST_FOLDER,
                                                                       settings.TEMP_DIR_OUTPUT)
    if not os.path.exists(request.file_path):
        raise ValueError(f"Path {request.file_path} does not exist")
    
    settings.TRANSCRIBER_TYPE = "test_api"
    settings.STORAGE_TYPE = "local"
    response = transcribe_file_endpoint(client, route, request=request)
    
    assert response.status_code == status_code
    data = response.json()
    path_normalized = os.path.normpath(data["file_path"])
    correctdir_normalized = os.path.normpath(correct_response.file_path)
    #Check that the returned path is inside the expected output directory
    assert os.path.commonpath([path_normalized, correctdir_normalized]) == correctdir_normalized 
   


@pytest.mark.parametrize("testing_case", td.wrong_testing_data, ids=[c["name"] for c in td.wrong_testing_data])
def test_wrong_cases(client, testing_case, settings):
    """
    Unhappy paths: tests various error scenarios
    """

   
    
    correct_response: Union[ResponseData, Message]
    request, correct_response, route, status_code = prepare_case_input(testing_case, 
                                                                       settings.TEST_FOLDER,
                                                                       settings.TEMP_DIR_OUTPUT)
    
    

    settings.TRANSCRIBER_TYPE = "test_api"
    settings.STORAGE_TYPE = "local"

    response = transcribe_file_endpoint(client, route, request=request)
    assert response.status_code == status_code
    data = response.json()
    assert data["code"] == correct_response.code

@pytest.mark.parametrize("testing_case", td.not_implemented_testing_data, ids=[c["name"] for c in td.not_implemented_testing_data])
def test_not_implemented(client, testing_case, settings):
    """
    Unhappy paths: tests various error scenarios
    """


    
    correct_response: Union[ResponseData, Message]
    request, correct_response, route, status_code = prepare_case_input(testing_case, 
                                                                       settings.TEST_FOLDER,
                                                                       settings.TEMP_DIR_OUTPUT)
    
    
    if testing_case["name"] == "test_file_manager_not_implemented":
        settings.STORAGE_TYPE = "unknown"
        settings.TRANSCRIBER_TYPE = "test_api"
    elif testing_case["name"] == "test_transcriber_not_implemented":
        settings.TRANSCRIBER_TYPE = "unknown"
        settings.STORAGE_TYPE = "local" 

    response = transcribe_file_endpoint(client, route, request=request)
    assert response.status_code == status_code
    data = response.json()
    assert data["code"] == correct_response.code




def test_internal_error(client, settings):
    """
     Simulates internal error during transcribing
    """

    testing_case = td.internal_error_testing_data[0]
    correct_response: Union[ResponseData, Message]
    request, correct_response, route, status_code = prepare_case_input(testing_case, 
                                                                       settings.TEST_FOLDER,
                                                                       settings.TEMP_DIR_OUTPUT)


    # replace get_transcriber() with a fake function
    settings.TRANSCRIBER_TYPE = "test_api"
    settings.STORAGE_TYPE = "local"
    with patch("app.api.routers.get_transcriber") as mock_get: 
        mock_transcriber = mock_get.return_value
        mock_transcriber.transcribe.side_effect = Exception("Simulated crash")
        response = transcribe_file_endpoint(client, route, request=request)

    assert response.status_code == status_code
    data = response.json()
    assert data["code"] == correct_response.code

#pytest tests/integration/test_transcribe_file.py -v


