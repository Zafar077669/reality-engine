from django.shortcuts import render

# Create your views here.
from drf_spectacular.utils import extend_schema

from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from users.mixins import CompanyQuerysetMixin
from .models import Event
from .serializers import EventSerializer

from audit.services import create_audit_log

@extend_schema(tags=['Events']) # Swaggerda alohida bo'lim qilib ko'rsatadi
class EventListCreateView(CompanyQuerysetMixin, ListCreateAPIView):

class EventListCreateView(
    CompanyQuerysetMixin,
    ListCreateAPIView
):
    """
    GET  → faqat o‘z company eventlari
    POST → event user.company ga ulanadi
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        event = serializer.save(company=self.request.user.company)

        create_audit_log(
            user=self.request.user,
            company=self.request.user.company,
            action="event_created",
            object_type="Event",
            object_id=event.id,
            metadata={"event_type": event.event_type},
            request=self.request,
        )
