import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_internal_error_format():
    client = APIClient()

    # mavjud bo‘lmagan endpoint
    response = client.get("/api/v1/unknown-endpoint/")

    assert response.status_code == 404
    assert "error" in response.json()
    assert "request_id" in response.json()