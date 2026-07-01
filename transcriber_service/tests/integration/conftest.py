"""
conftest.py

Pytest fixtures for integration tests: app setup, test client, and isolated test environment.
"""

from app import create_app
from tests.test_settings import TestSettings
import pytest
import shutil
import time
from fastapi.testclient import TestClient
import os

@pytest.fixture(scope="function")
def settings():
    """
    regenerates setting for each test
    """

    s = TestSettings.generate()
    yield s
    time.sleep(0.1)
    shutil.rmtree(s.TEMP_DIR_OUTPUT, ignore_errors=True)



@pytest.fixture(scope="function")
def app(settings): 
    return create_app(settings)


@pytest.fixture()
def client(app):
    # Set raise_server_exceptions=False to return JSON 500 responses
    # instead of letting unhandled exceptions crash the test
    return TestClient(app, raise_server_exceptions=False) 

