from fastapi.testclient import TestClient

from inspector.backend.core.config import settings


def test_api_root(rest_client: TestClient):
    request = rest_client.get(f"{settings.API_DEV_STR}")
    request.raise_for_status()
