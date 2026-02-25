from rest_framework.generics import ListAPIView, CreateAPIView
from signals.models import Signal
from api.serializers import SignalSerializer
from api.mixins import CompanyQuerySetMixin


class SignalListAPIView(CompanyQuerySetMixin, ListAPIView):
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer