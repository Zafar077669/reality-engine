import pytest
from django.conf import settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from companies.models import Company

User = get_user_model()


@pytest.mark.django_db
def test_enterprise_429_format(settings):
    # 🔥 FAqat burst_user rate ni o'zgartiramiz
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["burst_user"] = "1/min"

    company = Company.objects.create(name="TestCo", size=50)

    user = User.objects.create_user(
        username="test",
        password="pass1234",
        company=company,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    # 1-request OK
    r1 = client.get("/api/v1/signals/")
    assert r1.status_code == 200

    # 2-request → 429
    r2 = client.get("/api/v1/signals/")
    assert r2.status_code == 429

    data = r2.json()
    assert "error" in data
    assert "request_id" in data