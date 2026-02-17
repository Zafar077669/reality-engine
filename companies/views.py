from django.shortcuts import render

# Create your views here.
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from api.mixins import CompanyScopedQuerysetMixin
from users.permissions import IsAdminOrManager, IsSameCompany
from .models import Company
from .serializers import CompanySerializer


# =====================================================
# COMPANY LIST & CREATE
# =====================================================
class CompanyListCreateView(
    CompanyScopedQuerysetMixin,
    ListCreateAPIView
):
    """
    GET:
      - Admin → barcha companylar
      - Manager → faqat o‘z companysi

    POST:
      - Faqat Admin / Manager
      - Yangi company yaratish
    """

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def perform_create(self, serializer):
        # Company parent entity → company field yo‘q
        serializer.save()


# =====================================================
# COMPANY DETAIL / UPDATE / DELETE
# =====================================================
class CompanyDetailView(
    CompanyScopedQuerysetMixin,
    RetrieveUpdateDestroyAPIView
):
    """
    Object-level security:
    - Admin → hammasi
    - Manager → faqat o‘z companysi
    """

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [
        IsAuthenticated,
        IsAdminOrManager,
        IsSameCompany,
    ]
