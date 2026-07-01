"""
conftest.py

Pytest fixtures for integration tests: app setup, test client, and isolated test environment.
"""

from app import create_app
from tests.testing_settings import TestSettings
import pytest
import shutil
import time
from fastapi.testclient import TestClient
import os
from pymongo import MongoClient
from unittest.mock import patch, Mock

s = TestSettings.generate()
db_client = MongoClient(s.mongo_url)
testing_db = db_client.get_database(s.db_name)
testing_jobs_collection = testing_db.get_collection(s.collection_name)


def assert_test_db(settings):
    if "test" not in settings.db_name.lower():
        raise RuntimeError(
            f"Refusing to run tests on non-test database: {settings.db_name}"
        )

    if "test" not in settings.collection_name.lower():
        raise RuntimeError(
            f"Refusing to run tests on non-test collection: {settings.collection_name}"
        )

@pytest.fixture(scope="function")
def settings():

    
    s = TestSettings.generate()
    assert_test_db(s)

    db_client = MongoClient(s.mongo_url)
    testing_db = db_client.get_database(s.db_name)
    testing_jobs_collection = testing_db.get_collection(s.collection_name)

    testing_jobs_collection.delete_many({})

    yield s

    testing_jobs_collection.delete_many({})
    db_client.close()
    #shutil.rmtree(s.TEMP_DIR_OUTPUT, ignore_errors=True)



@pytest.fixture(scope="function")
def app(settings, mock_pipeline_clients): 
    return create_app(settings)


@pytest.fixture()
def client(app):
    # Set raise_server_exceptions=False to return JSON 500 responses
    # instead of letting unhandled exceptions crash the test
    return TestClient(app, raise_server_exceptions=False) 



@pytest.fixture
def mock_pipeline_clients():
    with (
        patch("app.services.job_pipeline.M.DownloaderClient") as MockDownloader,
        patch("app.services.job_pipeline.M.ConverterClient") as MockConverter,
        patch("app.services.job_pipeline.M.TranscriberClient") as MockTranscriber,
    ):
        yield MockDownloader, MockConverter, MockTranscriber

