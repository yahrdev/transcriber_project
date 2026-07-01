"""
conftest.py

Pytest fixtures for web_ui_service integration tests.
"""

import pytest

from app import create_app
from tests.testing_settings import TestSettings


@pytest.fixture(scope="function")
def settings():
    return TestSettings.generate()


@pytest.fixture(scope="function")
def app(settings):
    flask_app = create_app(settings)

    flask_app.config["TESTING"] = True
    flask_app.config["PROPAGATE_EXCEPTIONS"] = False

    return flask_app


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()