from rest_framework.generics import CreateAPIView
from events.models import Event
from api.serializers import EventSerializer
from api.mixins import CompanyQuerySetMixin


class EventCreateAPIView(CompanyQuerySetMixin, CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer