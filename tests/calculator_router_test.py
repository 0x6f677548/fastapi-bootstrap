from fastapi.testclient import TestClient
from fastapi_bootstrap.api_server.app import app
from fastapi_bootstrap.api_server.routers.authentication import is_turnstile_valid
import os

client = TestClient(app)


def test_calculator_addition():
    # Prepare headers with a valid API key from the environment
    headers = {"X-API-Key": os.environ.get("API_SERVER_API_KEY")}

    response = client.post("/calculator/add", headers=headers, json={"a": 1, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 3}


def test_calculator_addition_submit():
    # Mock the API key dependency
    app.dependency_overrides[is_turnstile_valid] = is_turnstile_valid_mock

    response = client.post("/calculator/add/submit", data={"a": 1, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 3}
    app.dependency_overrides.clear()


def test_calculator_subtraction():
    headers = {"X-API-Key": os.environ.get("API_SERVER_API_KEY")}

    response = client.post("/calculator/subtract", headers=headers, json={"a": 2, "b": 1})
    assert response.status_code == 200
    assert response.json() == {"result": 1}


def test_calculator_subtraction_submit():
    # Mock the API key dependency
    app.dependency_overrides[is_turnstile_valid] = is_turnstile_valid_mock

    response = client.post("/calculator/subtract/submit", data={"a": 2, "b": 1})
    assert response.status_code == 200
    assert response.json() == {"result": 1}
    app.dependency_overrides.clear()


def test_calculator_multiplication():
    headers = {"X-API-Key": os.environ.get("API_SERVER_API_KEY")}

    response = client.post("/calculator/multiply", headers=headers, json={"a": 2, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 6}


def test_calculator_multiplication_submit():
    # Mock the API key dependency
    app.dependency_overrides[is_turnstile_valid] = is_turnstile_valid_mock

    response = client.post("/calculator/multiply/submit", data={"a": 2, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 6}
    app.dependency_overrides.clear()


def test_calculator_division():
    headers = {"X-API-Key": os.environ.get("API_SERVER_API_KEY")}

    response = client.post("/calculator/divide", headers=headers, json={"a": 6, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 2}


async def is_turnstile_valid_mock():
    return True


def test_calculator_division_submit():
    # Mock the API key dependency
    app.dependency_overrides[is_turnstile_valid] = is_turnstile_valid_mock

    response = client.post("/calculator/divide/submit", data={"a": 6, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 2}
    app.dependency_overrides.clear()


def test_calculator_division_by_zero():
    headers = {"X-API-Key": os.environ.get("API_SERVER_API_KEY")}

    response = client.post("/calculator/divide", headers=headers, json={"a": 6, "b": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "Division by zero is not allowed."}


def test_calculator_division_by_zero_submit():
    # Mock the API key dependency
    app.dependency_overrides[is_turnstile_valid] = is_turnstile_valid_mock

    response = client.post("/calculator/divide/submit", data={"a": 6, "b": 0})
    assert response.status_code == 400
    assert response.json() == {"detail": "Division by zero is not allowed."}
    app.dependency_overrides.clear()
