import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled

logger = logging.getLogger("reality_engine")


def custom_exception_handler(exc, context):
    request = context.get("request")
    request_id = getattr(request, "request_id", None)

    # 1️⃣ DRF default handler
    response = drf_exception_handler(exc, context)

    # 2️⃣ AGAR DRF response BOR bo‘lsa
    if response is not None:

        # 🔥 429 — RATE LIMIT CASE
        if isinstance(exc, Throttled):
            retry_after = getattr(exc, "wait", None)

            # 🔍 AUDIT HOOK
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "request_id": request_id,
                    "path": request.path if request else None,
                    "method": request.method if request else None,
                    "retry_after": retry_after,
                },
            )

            return Response(
                {
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests",
                    "retry_after": retry_after,
                    "request_id": request_id,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Retry-After": str(retry_after) if retry_after else None
                },
            )

        # 🟡 BOSHQA 4xx / 5xx
        return Response(
            {
                "error": response.status_text.lower().replace(" ", "_"),
                "message": response.data,
                "request_id": request_id,
            },
            status=response.status_code,
        )

    # 3️⃣ 500 — UNHANDLED ERROR
    logger.exception(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "path": request.path if request else None,
            "method": request.method if request else None,
        },
    )

    return Response(
        {
            "error": "internal_error",
            "message": "Unexpected error occurred",
            "request_id": request_id,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )