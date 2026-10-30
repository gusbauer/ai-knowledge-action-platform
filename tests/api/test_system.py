from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert (
        body["message"]
        == "AI Knowledge & Action Platform API"
    )

    assert "environment" in body


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert "environment" in body
    
def test_request_id_is_returned():
    request_id = (
        "test-request-123"
    )

    response = client.get(
        "/health",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert (
        response.status_code == 200
    )

    assert (
        response.headers[
            "X-Request-ID"
        ]
        == request_id
    )