"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from api.views.health import HealthCheckView, ReadinessCheckView


def handler404(request, exception):
    request_id = getattr(request, "request_id", None)
    return JsonResponse(
        {
            "error": "not_found",
            "message": "Endpoint not found",
            "request_id": request_id,
        },
        status=404,
    )


urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ GLOBAL HEALTH — DRF ONLY
    path("health/", HealthCheckView.as_view()),
    path("ready/", ReadinessCheckView.as_view()),

    path("api/v1/", include("api.urls")),
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/infra/", include("infra.urls")),
    path("api/v1/incidents/", include("incidents.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema")),
]

