import pytest
from webnyx.app import WebNyxApp


@pytest.fixture
def app():
    return WebNyxApp()


@pytest.fixture
def test_client(app):
    return app.test_session()
