connections_success_case = {
        "response_status_code": 200,
        "response_json": {
            "file_path": "/tmp/result.wav",
            "file_name": "result",
            "file_extension": "wav",
        },
        "response_json_error": None,
        "requests_exception": None,
        "expected_result": "response_model",
        "expected_error": "",
    }

connections_microservice_unavailable_case = {
        "response_status_code": None,
        "response_json": None,
        "response_json_error": None,
        "requests_exception": "ConnectionError",
        "expected_result": None,
        "expected_error": "CONNECTION_ERROR",
    }



connections_wrong_responses_cases = {
    "response_is_not_json": {
        "response_status_code": 200,
        "response_json": None,
        "response_json_error": "JSONDecodeError",
        "requests_exception": None,
        "expected_result": None,
        "expected_error": "INVALID_JSON_RESPONSE",
    },

    "success_response_invalid_schema": {
        "response_status_code": 200,
        "response_json": {
            "wrong_field": "/tmp/result.wav",
        },
        "response_json_error": None,
        "requests_exception": None,
        "expected_result": None,
        "expected_error": "RESPONSE_VALIDATION_ERROR",
    }
}

connections_wrong_error_response_case =  {
        "response_status_code": 500,
        "response_json": {
            "unexpected": "format",
        },
        "response_json_error": None,
        "requests_exception": None,
        "expected_result": None,
        "expected_error": "INVALID_ERROR_RESPONSE",
    }



connections_upstream_errors_cases = {
    "upstream_400_valid_error_response": {
        "response_status_code": 400,
        "response_json":  {
                "message": "File has wrong type",
                "code": "FILE_WRONG_TYPE"
            }
        ,
        "response_json_error": None,
        "requests_exception": None,
        "expected_result": None,
        "upstream_error_code": "FILE_WRONG_TYPE",
        "expected_exception": "MicroserviceError",
        "expected_error_code": 500,
    },

    "upstream_500_valid_error_response": {
        "response_status_code": 500,
        "response_json":  {
                "message": "Internal service error",
                "code": "INTERNAL_ERROR"
            },
        "response_json_error": None,
        "requests_exception": None,
        "expected_result": None,
        "upstream_error_code": "INTERNAL_ERROR",
        "expected_exception": "MicroserviceError",
        "expected_error_code": 500,
    },

   
}
