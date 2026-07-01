validate_language_test_cases = {
    "valid_lowercase": {
        "input": "uk",
        "expected": "uk"
    },

    "valid_uppercase": {
        "input": "EN",
        "expected": "en"
    },

    "invalid_with_number": {
        "input": "uk7",
        "expected_error": "INVALID_LANGUAGE_FORMAT"
    },

    "empty_string": {
        "input": "",
        "expected": ""
    }
}


validate_media_mime_test_cases = {
    "video_bytes_success": {
        "source_type": "bytes",
        "filepath": "{filepath}",
        "expected_error": "",
    },
    "txt_bytes_wrong_type": {
        "source_type": "bytes",
        "filepath": "{filepath}",
        "expected_error": "FILE_WRONG_TYPE",
    },
    "video_path_success": {
        "source_type": "path",
        "filepath": "{filepath}",
        "expected_error": "",
    },
    "txt_path_wrong_type": {
        "source_type": "path",
        "filepath": "{filepath}",
        "expected_error": "FILE_WRONG_TYPE",
    },
}


validate_media_file_test_cases = {
    "valid_media_file": {
        "filepath": "{filepath}",
        "expected_error": "",
    },

    "corrupted_media_file": {
        "filepath": "{filepath}",
        "expected_error": "FILE_CORRUPTED",
    },
}