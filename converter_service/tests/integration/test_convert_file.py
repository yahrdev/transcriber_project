"""
test_convert_file.py

Tests for the /convert endpoint.
"""

import pytest
from tests.integration.data.convert_file_test_cases import testing_data
from unittest.mock import patch
import os
from tests.integration.helpers.utils import (
                            convert_file_endpoint,
                            create_dummy_file,
                            get_case,
                            prepare_case_input,
                            assert_error_response,
                            prepare_wrong_type,
                            skip_case,
                            prepare_folder
                        )


def test_200_case(client, settings):
    """"
    Happy path: successful conversion
    """
    
    testing_case = get_case("test_200_case")

    kwargs, target_filename_with_ext = prepare_case_input(settings, testing_case)
    create_dummy_file(kwargs["file_path"])

    response = convert_file_endpoint(client, **kwargs)
    assert response.status_code == 200
    data = response.get_json()
    expected_path = os.path.join(
    settings.TEMP_DIR_OUTPUT,
    target_filename_with_ext
    )

    assert data["file_path"] == expected_path



case_handlers = {
    "test_file_wrong_type": (prepare_wrong_type, lambda kwargs: kwargs["file_path"]),
    "test_file_not_found_path": (lambda _: None, lambda _: None),
    "test_internal_error": (skip_case, lambda _: None),
    "test_200_case": (skip_case, lambda _: None),
    "test_invalid_file_path": (prepare_folder, lambda kwargs: kwargs["file_path"])
}


@pytest.mark.parametrize("testing_case", testing_data, ids=[c["name"] for c in testing_data])
def test_wrong_cases(client, settings, testing_case):
    """
    Unhappy paths: tests various error scenarios
    """
    
    kwargs, _ = prepare_case_input(settings, testing_case)
    
    handler = case_handlers.get(testing_case["name"])
    if handler:
        func, get_param = handler
        param = get_param(kwargs)
        if func(param) == "SKIP":
            return
    else:
        create_dummy_file(kwargs["file_path"])

    response = convert_file_endpoint(client, **kwargs)
    assert_error_response(response, testing_case["status_code"], testing_case["custom_code"])



def test_internal_error(client, settings):
    """
    Simulates internal error during conversion
    """

    testing_case = get_case("test_internal_error")
    kwargs, _ = prepare_case_input(settings, testing_case)

    create_dummy_file(kwargs["file_path"])

    # replace get_convertator() with a fake function
    with patch("app.api.routers.get_convertator") as mock_get: 
        mock_converter = mock_get.return_value
        mock_converter.convert.side_effect = Exception("Simulated crash")
        response = convert_file_endpoint(client, **kwargs)

    assert_error_response(response, testing_case["status_code"], testing_case["custom_code"])


#pytest tests/integration/test_convert_file.py -v

