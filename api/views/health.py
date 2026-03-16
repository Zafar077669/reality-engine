import time
import logging

from django.db import connection
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

try:
    import redis
except ImportError:
    redis = None


logger = logging.getLogger("reality_engine")


class HealthCheckView(APIView):
    """
    Liveness probe (PUBLIC, INFRA)
    ❗ Hech qachon rate-limit bo‘lmaydi
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = []  # ✅ MUHIM: butunlay o‘chiq

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "reality-engine",
                "checks": {},
            },
            status=200,
        )


class ReadinessCheckView(APIView):
    """
    Readiness probe — dependency tekshiradi
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = []  # infra endpoint

    def get(self, request):
        start_time = time.time()

        db_ok, db_error = self._check_database()
        redis_ok, redis_error = self._check_redis()

        overall_ok = db_ok and redis_ok
        status_code = 200 if overall_ok else 503

        response = {
            "status": "ok" if overall_ok else "degraded",
            "checks": {
                "database": {
                    "ok": db_ok,
                    "error": db_error,
                },
                "redis": {
                    "ok": redis_ok,
                    "error": redis_error,
                },
            },
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
        }

        if not overall_ok:
            logger.error("Readiness check failed", extra=response)

        return Response(response, status=status_code)

    def _check_database(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
            return True, None
        except Exception as e:
            return False, str(e)

    def _check_redis(self):
        if not getattr(settings, "REDIS_URL", None):
            return True, "not_configured"

        if redis is None:
            return False, "redis_not_installed"

        try:
            r = redis.Redis.from_url(settings.REDIS_URL)
            r.ping()
            return True, None
        except Exception as e:
            return False, str(e)