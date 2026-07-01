testing_data = [
    {
        "name": "test_200_case",
        "route": "/download",
        "data": {
            "source_type": "url",
            "source": "https://samplelib.com/preview/mp4/sample-5s.mp4",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 200,
        "expected_response": {
            "file_path": "<settings.TEMP_DIR_OUTPUT> + '/' + file_name + '.' + file_extension",
            "file_name": "",
            "file_extension": "mp4"
        }
    },
    {
        "name": "test_file_not_found_path",
        "route": "/download",
        "data": {
            "source_type": "path",
            "source": "/nonexistent/testfile.mp4",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 404,
        "expected_response": {
            "message": "any non-empty string",
            "code": "FILE_NOT_FOUND_PATH"
        }
    },
    {
        "name": "test_invalid_file_path",
        "route": "/download",
        "data": {
            "source_type": "path",
            "source": "folder_only/",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 422,
        "expected_response": {
            "message": "any non-empty string",
            "code": "INVALID_FILE_PATH"
        }
    },
    {
        "name": "test_unsupported_extension",
        "route": "/download",
        "data": {
            "source_type": "path",
            "source": "/some/path/file.unsupported",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 422,
        "expected_response": {
            "message": "any non-empty string",
            "code": "UNSUPPORTED_EXTENSION"
        }
    },
    {
        "name": "test_url_unreachable",
        "route": "/download",
        "data": {
            "source_type": "url",
            "source": "https://filesamples.com/samples/video/mp4/sampl0.mp4",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 404,
        "expected_response": {
            "message": "any non-empty string",
            "code": "URL_UNREACHABLE"
        }
    },
    {
        "name": "test_not_url_when_expected",
        "route": "/download",
        "data": {
            "source_type": "url",
            "source": "/local/path/file.mp4",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 422,
        "expected_response": {
            "message": "any non-empty string",
            "code": "NOT_URL"
        }
    },
    {
        "name": "test_wrong_source_type",
        "route": "/download",
        "data": {
            "source_type": "ftp",
            "source": "ftp://example.com/file.mp4",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 400,
        "expected_response": {
            "message": "any non-empty string",
            "code": "BAD_REQUEST"
        }
    },
    {
        "name": "test_validation_error_missing_source",
        "route": "/download",
        "data": {
            "source_type": "url",
            "source": "",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 400,
        "expected_response": {
            "message": "list of field errors",
            "code": "BAD_REQUEST"
        }
    },
    {
        "name": "test_validation_error_missing_type",
        "route": "/download",
        "data": {
            "source_type": "",
            "source": "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 400,
        "expected_response": {
            "message": "list of field errors",
            "code": "BAD_REQUEST"
        }
    },
    {
        "name": "test_internal_error",
        "route": "/download",
        "data": {
            "source_type": "url",
            "source": "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "auth": {
                "method": "none"
            }
        },
        "status_code": 500,
        "expected_response": {
            "message":  "any non-empty string",
            "code": "INTERNAL_ERROR"
        }
    }
]
