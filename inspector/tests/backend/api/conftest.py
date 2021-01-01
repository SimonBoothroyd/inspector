import pytest
from fastapi.testclient import TestClient

from inspector.backend.app import app


@pytest.yield_fixture
def rest_client() -> TestClient:
    """Returns FastAPI test client."""

    with TestClient(app) as client:
        yield client
