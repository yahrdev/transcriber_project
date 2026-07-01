"""
conftest.py

Pytest fixtures for integration tests: app setup, test client, and isolated test environment.
"""

from app import create_app
from test_settings import TestSettings
import pytest
import shutil
import time

@pytest.fixture(scope="function")
def settings():
    """
    regenerates setting for each test
    """

    s = TestSettings.generate()
    yield s
    time.sleep(0.1)
    shutil.rmtree(s.TEMP_DIR_OUTPUT)


@pytest.fixture(scope="function")
def app(settings): 
    return create_app(settings)


@pytest.fixture()
def client(app):
    app.testing = True
    return app.test_client()

