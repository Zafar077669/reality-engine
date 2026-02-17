import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from companies.models import Company

User = get_user_model()

@pytest.fixture
def api_client():
    """Rest Framework API klienti - so'rovlarni yuborish uchun"""
    return APIClient()

@pytest.fixture
def company_factory(db):
    """
    Kompaniya yaratuvchi yordamchi.
    Modelingdagi PositiveIntegerField va NOT NULL cheklovlari inobatga olingan.
    """
    def create_company(name="Test Corp", industry="Tech", size=100):
        # size=100 berildi, chunki modelingda bu maydon IntegerField
        return Company.objects.create(
            name=name,
            industry=industry,
            size=size
        )
    return create_company

@pytest.fixture
def user_factory(db):
    """Foydalanuvchi yaratuvchi yordamchi - barcha role va company bog'lamalari bilan"""
    def create_user(username="test_user", company=None, role="company_user"):
        return User.objects.create_user(
            username=username,
            password="password123",
            company=company,
            role=role
        )
    return create_user