success_testing_data = [
    {
        "name": "test_200_case_default_params",
        "route": "/transcribe",
        "data": {
            "file_path": "Recording-test.mp3",
            "file_name": "Transcribed",
            "target_extension": "",
            "language": ""
        },
        "status_code": 200,
        "expected_response": {
            "file_path": "{TEMP_DIR_OUTPUT}/{file_name}.txt"
        }
    },
    {
        "name": "test_200_case_custom_params",
        "route": "/transcribe",
        "data": {
            "file_path": "Recording-test.mp3",
            "file_name": "Transcribed",
            "target_extension": "pdf",
            "language": "ua"
        },
        "status_code": 200,
        "expected_response": {
            "file_path": "{TEMP_DIR_OUTPUT}/{file_name}.pdf"
        }
    }

]

wrong_testing_data = [
    {
        "name": "test_file_not_found_path",
        "route": "/transcribe",
        "data": {
            "file_path": "Recording-test_1.mp3",
            "file_name": "Transcribed",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 404,
        "expected_response": {
            "message": "any non-empty string",
            "code": "FILE_NOT_FOUND_PATH"
        }
    },
    {
        "name": "test_unsupported_extension",
        "route": "/transcribe",
        "data": {
            "file_path": "Text-test.txt",
            "file_name": "Transcribed",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 422,
        "expected_response": {
            "message": "any non-empty string",
            "code": "UNSUPPORTED_EXTENSION"
        }
    },
    {
        "name": "test_validation_error_empty_file_path",
        "route": "/transcribe",
        "data": {
            "file_path": "",
            "file_name": "Transcribed",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 400,
        "expected_response": {
            "message": "list of field errors",
            "code": "BAD_REQUEST"
        }
    },
    {
        "name": "test_validation_error_empty_file_name",
        "route": "/transcribe",
        "data": {
            "file_path": "Recording-test.mp3",
            "file_name": "",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 400,
        "expected_response": {
            "message": "list of field errors",
            "code": "BAD_REQUEST"
        }
    },
    {
        "name": "test_validation_error_missing_file_path",
        "route": "/transcribe",
        "data": {
            "file_name": "Transcribed",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 400,
        "expected_response": {
            "message": "list of field errors",
            "code": "BAD_REQUEST"
        }
    },
    {
        "name": "test_validation_error_missing_file_name",
        "route": "/transcribe",
        "data": {
            "file_path": "Recording-test.mp3",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 400,
        "expected_response": {
            "message": "list of field errors",
            "code": "BAD_REQUEST"
        }
    },
    {
        "name": "test_validation_error_invalid_json",
        "route": "/transcribe",
        "data": "{invalid_json}",
        "status_code": 400,
        "expected_response": {
            "message": "list of field errors",
            "code": "BAD_REQUEST"
        }
    }

]

not_implemented_testing_data = [
    {
        "name": "test_transcriber_not_implemented",
        "route": "/transcribe",
        "data": {
            "file_path": "Recording-test.mp3",
            "file_name": "Transcribed",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 422,
        "expected_response": {
            "message": "any non-empty string",
            "code": "TRANSCRIBER_NOT_IMPLEMENTED"
        }
    },
    {
        "name": "test_file_manager_not_implemented",
        "route": "/transcribe",
        "data": {
            "file_path": "Recording-test.mp3",
            "file_name": "Transcribed",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 422,
        "expected_response": {
            "message": "any non-empty string",
            "code": "FILE_MANAGER_NOT_IMPLEMENTED"
        }
    }
]


internal_error_testing_data = [
    
    
    {
        "name": "test_internal_error",
        "route": "/transcribe",
        "data": {
            "file_path": "Recording-test.mp3",
            "file_name": "Transcribed",
            "target_extension": "txt",
            "language": "uk"
        },
        "status_code": 500,
        "expected_response": {
            "message": "any non-empty string",
            "code": "INTERNAL_ERROR"
        }
    }
    
]