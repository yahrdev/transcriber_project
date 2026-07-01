"""
convert_file_test_cases.py

Contains test case definitions for various success and error scenarios in file conversion.
"""

testing_data = [
    {
        "name": "test_200_case",
        "route": "",
        "data": {
            "filename_with_ext": "test.mp4",
            "target_filename": "test_result",
            "source_extension": "mp4",
            "target_extension": "wav"
        },
        "status_code": 200,
        "custom_code": ""
    },
    {
        "name": "test_file_wrong_type",
        "route": "",
        "data": {
            "filename_with_ext": "test.mp4",
            "target_filename": "test_result",
            "source_extension": "mp4",
            "target_extension": "wav"
        },
        "status_code": 400,
        "custom_code": "FILE_WRONG_TYPE"
    },
    {
        "name": "test_wrong_conversion",
        "route": "",
        "data": {
            "filename_with_ext": "test.mp3",
            "target_filename": "test_result",
            "source_extension": "mp3",
            "target_extension": "mp4"
        },
        "status_code": 422,
        "custom_code": "WRONG_CONVERSION"
    },
    {
        "name": "test_file_not_found_path",
        "route": "",
        "data": {
            "filename_with_ext": "missing.mp4",
            "target_filename": "test_result",
            "source_extension": "mp4",
            "target_extension": "wav"
        },
        "status_code": 404,
        "custom_code": "FILE_NOT_FOUND_PATH"
    },
    {
        "name": "test_invalid_file_path",
        "route": "",
        "data": {
            "filename_with_ext": "folder_only/",
            "target_filename": "test_result",
            "source_extension": "mp4",
            "target_extension": "wav"
        },
        "status_code": 422,
        "custom_code": "INVALID_FILE_PATH"
    },
    {
        "name": "test_extension_mismatch",
        "route": "",
        "data": {
            "filename_with_ext": "test.mp4",
            "target_filename": "test_result",
            "source_extension": "mp3",  
            "target_extension": "wav"
        },
        "status_code": 422,
        "custom_code": "EXTENSION_MISMATCH"
    },
    {
        "name": "test_unsupported_extension",
        "route": "",
        "data": {
            "filename_with_ext": "test.xyz",
            "target_filename": "test_result",
            "source_extension": "xyz",
            "target_extension": "wav"
        },
        "status_code": 422,
        "custom_code": "UNSUPPORTED_EXTENSION"
    },
    {
        "name": "test_unsupported_target_extension",
        "route": "",
        "data": {
            "filename_with_ext": "test.mp4",
            "target_filename": "test_result",
            "source_extension": "mp4",
            "target_extension": "xyz"
        },
        "status_code": 422,
        "custom_code": "UNSUPPORTED_EXTENSION"
    },
    {
        "name": "test_internal_error",
        "route": "",
        "data": {
            "filename_with_ext": "test.mp4",
            "target_filename": "test_result",
            "source_extension": "mp4",
            "target_extension": "wav"
        },
        "status_code": 500,
        "custom_code": "INTERNAL_ERROR"
    },
    {
        "name": "test_route_not_found",
        "route": "/nonexistent/route",
        "data": {
            "filename_with_ext": "test.mp4",
            "target_filename": "test_result",
            "source_extension": "mp4",
            "target_extension": "wav"
        },
        "status_code": 404,
        "custom_code": "ROUTE_NOT_FOUND"
    },
    {
        "name": "test_validation_error",
        "route": "",
        "data": {
            "filename_with_ext": "test.mp4",
            "target_filename": "test_result",
            "source_extension": "",
            "target_extension": "wav"
        },
        "status_code": 400,
        "custom_code": "VALIDATION_ERROR"
    },
]
