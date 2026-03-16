from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from alerts.models import AlertHistory
from django.utils.timezone import now


class AcknowledgeAlertView(APIView):

    def post(self, request, pk):
        alert = AlertHistory.objects.get(pk=pk)

        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = now()
        alert.save()

        return Response({"status": "acknowledged"})