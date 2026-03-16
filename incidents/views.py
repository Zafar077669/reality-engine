from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from incidents.models import Incident
from incidents.services import IncidentService
from companies.models import CompanyMembership
from users.models import User


# ==========================================================
# INCIDENT LIST
# ==========================================================

class IncidentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        memberships = CompanyMembership.objects.filter(
            user=request.user
        ).values_list("company_id", flat=True)

        incidents = (
            Incident.objects
            .filter(company_id__in=memberships)
            .select_related("assigned_to", "company")
            .order_by("-created_at")
        )

        data = [
            {
                "id": i.id,
                "status": i.status,
                "assigned_to": i.assigned_to_id if i.assigned_to else None,
                "acknowledged_at": i.acknowledged_at,
                "ack_deadline_at": getattr(i, "ack_deadline_at", None),
                "escalation_level": i.escalation_level,
                "created_at": i.created_at,
            }
            for i in incidents
        ]

        return Response(data)


# ==========================================================
# ASSIGN INCIDENT
# ==========================================================

class IncidentAssignAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        memberships = CompanyMembership.objects.filter(
            user=request.user
        ).values_list("company_id", flat=True)

        incident = get_object_or_404(
            Incident,
            pk=pk,
            company_id__in=memberships
        )

        engineer_id = request.data.get("engineer_id")

        if not engineer_id:
            return Response(
                {"detail": "engineer_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        engineer_user = get_object_or_404(User, pk=engineer_id)

        try:
            IncidentService.assign_incident(
                actor=request.user,
                incident=incident,
                engineer_user=engineer_user
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response({"detail": "Incident assigned"})


# ==========================================================
# RESOLVE INCIDENT
# ==========================================================

class IncidentResolveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        memberships = CompanyMembership.objects.filter(
            user=request.user
        ).values_list("company_id", flat=True)

        incident = get_object_or_404(
            Incident,
            pk=pk,
            company_id__in=memberships
        )

        try:
            IncidentService.resolve_incident(
                actor=request.user,
                incident=incident
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response({"detail": "Incident resolved"})


# ==========================================================
# ACK INCIDENT
# ==========================================================

class IncidentAcknowledgeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        memberships = CompanyMembership.objects.filter(
            user=request.user
        ).values_list("company_id", flat=True)

        incident = get_object_or_404(
            Incident,
            pk=pk,
            company_id__in=memberships
        )

        try:
            IncidentService.acknowledge_incident(
                actor=request.user,
                incident=incident
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response({"detail": "Incident acknowledged"})