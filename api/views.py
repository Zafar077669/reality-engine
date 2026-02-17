from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from events.models import Event
from signals.models import Signal
from .serializers import EventSerializer, SignalSerializer


# EVENT CREATE (POST)
class EventCreateAPIView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# SIGNAL LIST (GET)
class SignalListAPIView(generics.ListAPIView):
    serializer_class = SignalSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # agar user company bilan bog'langan bo'lsa
        if hasattr(user, "company") and user.company:
            return Signal.objects.filter(
                company=user.company
            ).order_by("-detected_at")

        return Signal.objects.none()
