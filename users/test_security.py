import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from companies.models import Company
from signals.models import Signal
from signals.views import SignalListAPIView

User = get_user_model()


@pytest.mark.django_db
class TestMultiTenantSecurity:
    """
    Multi-tenant isolation test.
    Bu testda throttle view-level o‘chiriladi.
    """

    def test_user_cannot_see_other_company_signals(self, monkeypatch):
        # 🔥 VIEW-LEVEL THROTTLE NI O‘CHIRAMIZ
        monkeypatch.setattr(SignalListAPIView, "throttle_classes", [])

        # Companies
        comp_a = Company.objects.create(name="Company A", size=10)
        comp_b = Company.objects.create(name="Company B", size=20)

        # User faqat Company A ga tegishli
        user_a = User.objects.create_user(
            username="user_a",
            password="pass1234",
            company=comp_a,
        )

        # Signals
        Signal.objects.create(
            company=comp_a,
            response_time_ms=100,
            severity="high",
        )
        Signal.objects.create(
            company=comp_b,
            response_time_ms=100,
            severity="low",
        )

        client = APIClient()
        client.force_authenticate(user=user_a)

        response = client.get("/api/v1/signals/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # ✅ Pagination structure tekshiramiz
        assert "results" in data
        assert isinstance(data["results"], list)

        # 🔒 Faqat o‘z company signalini ko‘radi
        assert len(data["results"]) == 1
        assert data["results"][0]["company"] == comp_a.id