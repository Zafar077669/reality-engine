from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer, UserSerializer
from users.permissions import IsAdmin, IsAdminOrManager, IsSameCompany
from users.mixins import CompanyQuerysetMixin
from companies.models import Company
from rest_framework.generics import RetrieveAPIView

from audit.services import create_audit_log

User = get_user_model()


# =========================
# REGISTER
# =========================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        create_audit_log(
            user=user,
            company=user.company,
            action="register",
            object_type="User",
            object_id=user.id,
            request=request,
        )

        return Response(
            {
                "message": "User registered successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================
# LOGIN (JWT + AUDIT)
# =========================
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = User.objects.get(username=request.data["username"])

            create_audit_log(
                user=user,
                company=user.company,
                action="login",
                object_type="User",
                object_id=user.id,
                request=request,
            )

        return response


# =========================
# LOGOUT (JWT + AUDIT)
# =========================
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        create_audit_log(
            user=request.user,
            company=request.user.company,
            action="logout",
            object_type="User",
            object_id=request.user.id,
            request=request,
        )

        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_205_RESET_CONTENT,
        )


# =========================
# CURRENT USER
# =========================
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# =========================
# COMPANY DETAIL (SAFE)
# =========================
class CompanyDetailView(
    CompanyQuerysetMixin,
    RetrieveAPIView
):
    queryset = Company.objects.all()
    serializer_class = None
    permission_classes = [IsAdminOrManager, IsSameCompany]

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsAdmin, IsAdminOrManager


class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(
            {"message": "Admin access granted"},
            status=status.HTTP_200_OK,
        )


class AdminManagerView(APIView):
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        return Response(
            {"message": "Admin or Manager access granted"},
            status=status.HTTP_200_OK,
        )
