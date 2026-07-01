extension_test_cases = {
    "simple_extension": {
        "filename": "video.mp4",
        "expected": "mp4",
    },

    "multiple_dots": {
        "filename": "archive.test.mp4",
        "expected": "mp4",
    },

    "no_extension": {
        "filename": "file",
        "expected_error": "INVALID_FILE_EXTENSION",
    },

    "empty_string": {
        "filename": "",
        "expected_error": "INVALID_FILE_EXTENSION",
    },
}