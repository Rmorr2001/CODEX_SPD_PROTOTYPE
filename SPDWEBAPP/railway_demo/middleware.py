from django.http import JsonResponse


class DemoBoundaryMiddleware:
    """Allow original demo workflows while excluding public administrator access."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            return JsonResponse({"error": "Admin is unavailable on the public demo."}, status=403)
        return self.get_response(request)
