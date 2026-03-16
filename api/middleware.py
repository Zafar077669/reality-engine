import uuid
from django.utils.deprecation import MiddlewareMixin

class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.request_id = f"req-{uuid.uuid4().hex[:12]}"

    def process_response(self, request, response):
        request_id = getattr(request, "request_id", None)
        if request_id:
            response["X-Request-ID"] = request_id
        return response