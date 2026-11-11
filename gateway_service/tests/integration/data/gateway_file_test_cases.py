upload_endpoint_test_cases = {
    "valid_upload": {
        "disk_file": "testvideo.mp4",
        "upload_filename": "testvideo.mp4",
        "language": "en",
        "mock_pipeline_error": None,
        "expected_status_code": 202,
        "expected_fields": ["job_id", "data.result_url"],
    },

    "invalid_language": {
        "disk_file": "testvideo.mp4",
        "upload_filename": "testvideo.mp4",
        "language": "uk7",
        "mock_pipeline_error": None,
        "expected_status_code": 422,
        "expected_error_code": "INVALID_LANGUAGE_FORMAT",
    },

    "file_without_extension": {
        "disk_file": "testvideo.mp4",
        "upload_filename": "testvideo",
        "language": "en",
        "mock_pipeline_error": None,
        "expected_status_code": 422,
        "expected_error_code": "INVALID_FILE_EXTENSION",
    },

    "wrong_media_type": {
        "disk_file": "testtxt.txt",
        "upload_filename": "testtxt.txt",
        "language": "en",
        "mock_pipeline_error": None,
        "expected_status_code": 422,
        "expected_error_code": "FILE_WRONG_TYPE",
    },


}


reference_endpoint_test_cases = {
    "valid_reference": {
        "request_json": {
            "client_id": "test_client",
            "source_type": "path",
            "source": "testvideo.mp4",
            "language": "en",
        },
        "mock_pipeline_error": None,
        "expected_status_code": 202,
        "expected_fields": ["job_id", "data.result_url"],
    },

    "missing_client_id": {
        "request_json": {
            "source_type": "path",
            "source": "testvideo.mp4",
            "language": "en",
        },
        "mock_pipeline_error": None,
        "expected_status_code": 400,
        "expected_error_code": "BAD_REQUEST",
    },

    "missing_source": {
        "request_json": {
            "client_id": "test_client",
            "source_type": "path",
            "language": "en",
        },
        "mock_pipeline_error": None,
        "expected_status_code": 400,
        "expected_error_code": "BAD_REQUEST",
    },

    "missing_source_type": {
        "request_json": {
            "client_id": "test_client",
            "source": "testvideo.mp4",
            "language": "en",
        },
        "mock_pipeline_error": None,
        "expected_status_code": 400,
        "expected_error_code": "BAD_REQUEST",
    },

    "missing_language": {
        "request_json": {
            "client_id": "test_client",
            "source_type": "path",
            "source": "testvideo.mp4",
        },
        "mock_pipeline_error": None,
        "expected_status_code": 400,
        "expected_error_code": "BAD_REQUEST",
    },

    "invalid_language": {
        "request_json": {
            "client_id": "test_client",
            "source_type": "path",
            "source": "testvideo.mp4",
            "language": "uk7",
        },
        "mock_pipeline_error": None,
        "expected_status_code": 422,
        "expected_error_code": "INVALID_LANGUAGE_FORMAT",
    },

}


download_result_endpoint_test_cases = {
    "completed_job_existing_file": {
        "job_id": "existing_completed_job",
        "result_disk_file": "result.txt",
        "expected_status_code": 200,
        "expected_content_type": "text/plain",
    },

    "job_not_found": {
        "job_id": "missing_job",
        "expected_status_code": 500,
        "expected_error_code": "INTERNAL_ERROR",
    },

        "job_not_finished": {
        "expected_status_code": 409,
        "expected_error_code": "NOT_FINISHED",
    },

    "job_failed": {
        "expected_status_code": 409,
        "expected_error_code": "JOB_FAILED",
    },
}