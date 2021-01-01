import pytest
from pydantic import ValidationError

from inspector.backend.core.config import Settings


@pytest.mark.parametrize(
    "value, expected",
    [
        ('"http://localhost:4200"', ["http://localhost:4200"]),
        (
            '"http://localhost:4200, http://localhost:8200"',
            ["http://localhost:4200", "http://localhost:8200"],
        ),
    ],
)
def test_cors_validation(value, expected, monkeypatch):

    monkeypatch.setenv("BACKEND_CORS_ORIGINS", value)

    settings = Settings()
    assert settings.BACKEND_CORS_ORIGINS == expected


def test_cors_validation_error(monkeypatch):

    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "0")

    with pytest.raises(ValidationError):
        Settings()
