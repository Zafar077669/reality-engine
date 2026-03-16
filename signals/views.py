from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from users.mixins import CompanyQuerysetMixin
from alerts.services.alert_dispatcher import dispatch_alert

from .models import Signal
from .serializers import SignalSerializer


# =====================================
# 📄 SIGNAL LIST (GET)
# =====================================
class SignalListAPIView(CompanyQuerysetMixin, ListAPIView):
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["severity"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


# =====================================
# ➕ SIGNAL CREATE (POST)
# =====================================
class SignalCreateAPIView(CompanyQuerysetMixin, CreateAPIView):
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        ENTERPRISE LOGIC:
        - company avtomatik token orqali olinadi
        - client company yubormaydi
        - alert faqat critical signal uchun
        """

        # 1️⃣ Signalni saqlaymiz (company = token orqali)
        signal = serializer.save(
            company=self.request.user.company
        )

        # 2️⃣ FAQAT CRITICAL bo‘lsa alert yuboramiz
        if signal.severity == "critical":
            try:
                dispatch_alert(signal)
            except Exception as exc:
                # ❗ Alert xatosi API ni yiqitmasligi kerak
                import logging
                logger = logging.getLogger(__name__)
                logger.error(
                    f"Alert dispatch failed for signal_id={signal.id}: {exc}"
                )