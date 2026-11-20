import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_answers():
    # Hand-made test input, never a real check-in or research training row.
    return {"gender": "female", "age": 21, "faculty_group": "Health sciences", "year": 2,
            "cgpa_band": "3.00-3.49", "married": False, "anxiety": True,
            "panic": False, "specialist": False}
