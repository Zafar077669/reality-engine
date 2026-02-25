def test_health_endpoint(client):
    response = client.get("/health/")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "checks" in data