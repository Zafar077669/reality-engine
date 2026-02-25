import time
import logging

from django.db import connection
from django.http import JsonResponse
from django.conf import settings

try:
    import redis
except ImportError:
    redis = None


logger = logging.getLogger(__name__)


def check_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        return True, None
    except Exception as e:
        return False, str(e)


def check_redis():
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


def health_check(request):
    """
    Liveness probe — servis ishlayaptimi?
    """
    return JsonResponse(
        {
            "status": "ok",
            "service": "reality-engine",
        },
        status=200,
    )


def readiness_check(request):
    """
    Readiness probe — servis dependencylar tayyormi?
    """
    start_time = time.time()

    db_ok, db_error = check_database()
    redis_ok, redis_error = check_redis()

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

    return JsonResponse(response, status=status_code)