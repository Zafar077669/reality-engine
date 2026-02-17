from django.shortcuts import render

# Create your views here.
# signals/views.py
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter # Qidirish va tartiblash uchun
from django_filters.rest_framework import DjangoFilterBackend # Filtr uchun

from users.mixins import CompanyQuerysetMixin
from .models import Signal
from .serializers import SignalSerializer

class SignalListAPIView(CompanyQuerysetMixin, ListAPIView):
    """
    GET → Multi-tenant auto-filter
    Admin → barcha signallar
    Manager/User → faqat o‘z company signallari
    """
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer
    permission_classes = [IsAuthenticated]

    # Filtr backendlarini aynan shu view uchun ko'rsatamiz
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtrlash maydonlari
    filterset_fields = ['severity', 'is_resolved'] 
    
    # Qidirish maydonlari (message ichidan qidiradi)
    search_fields = ['message'] 
    
    # Tartiblash (default yaratilgan vaqti bo'yicha)
    ordering_fields = ['created_at']
    ordering = ['-created_at'] # Eng yangilari birinchi chiqadi